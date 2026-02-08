from typing import Optional
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
import os
import logging
from datetime import datetime, timezone

# Logger configuration
logger = logging.getLogger("api_gateway.auth")

# Initialize security scheme
security = HTTPBearer(auto_error=False)

# Configuration from environment
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://todo-frontend")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"
API_AUDIENCE = os.getenv("API_AUDIENCE", "http://localhost:8000")

# Initialize JWKS Client
# Lazy initialization to avoid startup failure if frontend isn't ready
_jwks_client = None

def get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        logger.info(f"Initializing JWKS Client with URL: {JWKS_URL}")
        _jwks_client = PyJWKClient(JWKS_URL)
    return _jwks_client

async def verify_token(token: str) -> dict:
    """
    Verify token:
    1. Try JWKS (EdDSA) - Default for Better Auth
    2. Try Shared Secret (HS256) - Fallback
    """
    
    # 1. Try JWKS Verification
    try:
        jwks = get_jwks_client()
        signing_key = jwks.get_signing_key_from_jwt(token)
        
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "RS256"],
            options={"verify_aud": False, "verify_iss": False}, # Relaxed for local dev
            leeway=120
        )
        logger.info(f"Successfully verified JWT (JWKS) for user {payload.get('sub')}")
        return payload
    except Exception as e:
        logger.warning(f"JWKS verification failed: {str(e)}")

    # 2. Try Shared Secret (HS256)
    if JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False, "verify_iss": False},
                leeway=120
            )
            logger.info(f"Successfully verified JWT (HS256) for user {payload.get('sub')}")
            return payload
        except Exception as e:
            logger.warning(f"HS256 verification failed: {str(e)}")

    # All failed
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token"
    )

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPBearer] = Depends(security)
) -> dict:
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    
    if not token:
        # Check for token in cookies as fallback (Better Auth uses cookies)
        token = request.cookies.get("better-auth.session_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing Authorization header or session cookie"
        )

    return await verify_token(token)
