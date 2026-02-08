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
from database import get_session
from models import Session

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize security scheme
security = HTTPBearer(auto_error=False)

# Configuration
def get_config():
    auth_url = os.getenv("BETTER_AUTH_URL", "http://todo-frontend")
    return {
        "JWT_SECRET": os.getenv("BETTER_AUTH_SECRET"),
        "BETTER_AUTH_URL": auth_url,
        "JWKS_URL": f"{auth_url}/api/auth/jwks",
        "API_AUDIENCE": os.getenv("API_AUDIENCE", "http://localhost:8000")
    }

# Lazy JWKS Client
_jwks_client = None

def get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        config = get_config()
        logger.info(f"Initializing JWKS Client with URL: {config['JWKS_URL']}")
        _jwks_client = PyJWKClient(config['JWKS_URL'])
    return _jwks_client

async def verify_token(token: str, db: AsyncSession) -> dict:
    """
    Verify token: 
    1. Try JWKS (EdDSA) - Default for Better Auth
    2. Try Shared Secret (HS256) - Fallback
    3. Try Opaque Session Token - Fallback
    """
    config = get_config()
    
    # DEBUG: Log token header to see what algorithm is being used
    try:
        unverified_header = jwt.get_unverified_header(token)
        logger.info(f"🔍 Token header: {unverified_header}")
        logger.info(f"🔑 JWT_SECRET configured: {bool(config['JWT_SECRET'])}")
        logger.info(f"🌐 JWKS_URL: {config['JWKS_URL']}")
    except Exception as e:
        logger.error(f"Failed to parse token header: {e}")
    
    # 1. Try JWKS Verification (EdDSA)
    try:
        client = get_jwks_client()
        # This automatically fetches keys and finds the right one by 'kid'
        signing_key = client.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "RS256"],
            # Relaxing issuer/audience check for local dev stability
            options={"verify_aud": False, "verify_iss": False},
            leeway=120 
        )
        logger.info(f"✅ Successfully verified JWT (JWKS) for user {payload.get('sub')}")
        return payload
    except Exception as e:
        logger.warning(f"JWKS verification failed: {str(e)}")

    # 2. Try Shared Secret Verification (HS256)
    if config['JWT_SECRET']:
        try:
            # First peek at the header to see the algorithm
            unverified_header = jwt.get_unverified_header(token)
            alg = unverified_header.get("alg")
            logger.info(f"Attempting HS256 verify. Token header: {unverified_header}")
            
            payload = jwt.decode(
                token,
                config['JWT_SECRET'],
                algorithms=["HS256", "EdDSA", "RS256"], # Allow fallback decoding
                options={"verify_aud": False, "verify_iss": False},
                leeway=120
            )
            logger.info(f"Successfully verified JWT ({alg}) for user {payload.get('sub')}")
            return payload
        except Exception as e:
            logger.warning(f"Shared secret verification failed ({type(e).__name__}): {str(e)}")

    # 3. Verify as Opaque Session Token in DB
    try:
        # ... (opaque logic) ...
        raw_token = token
        if "." in token:
             parts = token.split(".")
             if len(parts) == 2: # Typical signed cookie format: value.signature
                 raw_token = parts[0]
        
        statement = select(Session).where(Session.token == raw_token)
        result = await db.exec(statement)
        session = result.first()
        
        if session:
            # ... (expiry check) ...
            now = datetime.now(timezone.utc)
            session_expiry = session.expiresAt.replace(tzinfo=timezone.utc) if session.expiresAt.tzinfo is None else session.expiresAt
            
            if session_expiry < now:
                logger.warning(f"Session expired: {session_expiry} < {now}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return {
                "sub": session.userId,
                "type": "session",
                "exp": int(session.expiresAt.timestamp())
            }
        else:
             logger.warning(f"No session found in DB for token starting with {raw_token[:10]}...")
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
    """
    Extract and verify user token from:
    1. Authorization header (Bearer token)
    2. better-auth.session_token cookie (Better Auth default)
    """
    token = None
    
    # Try Authorization header first
    if credentials and credentials.credentials:
        token = credentials.credentials
    
    # If no Authorization header, try cookie
    if not token:
        # Better Auth stores session token in cookies
        token = request.cookies.get("better-auth.session_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing Authorization header or session cookie"
        )
    
    return await verify_token(token, db)

def create_access_token(data: dict, expires_delta: Optional[datetime] = None) -> str:
    # Use HS256 for self-issued tokens if needed
    config = get_config()
    if not config['JWT_SECRET']:
        raise ValueError("JWT secret not configured")

    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": expires_delta})

    return jwt.encode(to_encode, config['JWT_SECRET'], algorithm="HS256")