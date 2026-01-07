from typing import Optional
import jwt  # PyJWT
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .database import get_session
from .models import Session

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize security scheme
security = HTTPBearer(auto_error=False)

# Configuration
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"
API_AUDIENCE = os.getenv("API_AUDIENCE", "http://127.0.0.1:8000")

# Initialize JWKS Client
jwks_client = PyJWKClient(JWKS_URL)

async def verify_token(token: str, db: AsyncSession) -> dict:
    """
    Verify token: 
    1. Try JWKS (EdDSA) - Default for Better Auth
    2. Try Shared Secret (HS256) - Fallback
    3. Try Opaque Session Token - Fallback
    """
    
    # 1. Try JWKS Verification (EdDSA)
    try:
        # This automatically fetches keys and finds the right one by 'kid'
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "RS256"],
            audience=API_AUDIENCE,
            issuer=BETTER_AUTH_URL,
            # Allow some clock skew
            leeway=60 
        )
        logger.info(f"Successfully verified JWT (JWKS) for user {payload.get('sub')}")
        return payload
    except Exception as e:
        logger.warning(f"JWKS verification failed: {e}")

    # 2. Try Shared Secret Verification (HS256)
    if JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                audience=API_AUDIENCE,
                issuer=BETTER_AUTH_URL
            )
            logger.info(f"Successfully verified JWT (HS256) for user {payload.get('sub')}")
            return payload
        except Exception as e:
            logger.warning(f"HS256 verification failed: {e}")

    # 3. Verify as Opaque Session Token in DB
    try:
        # Better Auth sends signed cookies (e.g., token.signature)
        # We need to strip the signature to match the DB record
        # Use only the first part if it's a signed cookie (but NOT if it's a JWT which has 3 parts)
        # However, we already failed JWT check, so safe to assume it's opaque-like
        raw_token = token
        if "." in token:
             parts = token.split(".")
             if len(parts) == 2: # Typical signed cookie format: value.signature
                 raw_token = parts[0]
        
        statement = select(Session).where(Session.token == raw_token)
        result = await db.exec(statement)
        session = result.first()
        
        if session:
            now = datetime.now(timezone.utc)
            session_expiry = session.expiresAt.replace(tzinfo=timezone.utc) if session.expiresAt.tzinfo is None else session.expiresAt
            
            if session_expiry < now:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return {
                "sub": session.userId,
                "type": "session",
                "exp": int(session.expiresAt.timestamp())
            }
    except Exception as e:
        logger.error(f"Database session lookup error: {str(e)}")

    # All failed
    logger.warning("Token verification completely failed")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPBearer] = Depends(security),
    db: AsyncSession = Depends(get_session)
) -> dict:
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing Authorization header"
        )
    
    return await verify_token(token, db)

def create_access_token(data: dict, expires_delta: Optional[datetime] = None) -> str:
    # Use HS256 for self-issued tokens if needed
    if not JWT_SECRET:
        raise ValueError("JWT secret not configured")

    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": expires_delta})

    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")