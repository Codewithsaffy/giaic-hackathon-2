"""
Authentication and user extraction utilities.
Uses multi-user-data-isolation and better-auth-expert skills.
"""
from fastapi import Request, HTTPException
from src.shared.models import User
from uuid import UUID
import os
from jose import JWTError, jwt

def get_current_user(request: Request) -> User:
    """
    Extract current user from request.
    Supports multiple authentication methods:
    1. X-User-ID header (from Dapr/Gateway)
    2. JWT Bearer token
    3. Fallback to test user for development
    
    Following multi-user-data-isolation pattern.
    """
    # Try X-User-ID header first (from Dapr service invocation)
    user_id_str = request.headers.get("X-User-ID")
    if user_id_str:
        try:
            return User(
                id=UUID(user_id_str),
                username="authenticated_user",
                email=""
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid User ID format")
    
    # Try JWT Bearer token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        secret = os.getenv("BETTER_AUTH_SECRET", "fallback_secret")
        
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token: no user ID")
            
            return User(
                id=UUID(user_id),
                username=payload.get("name", "jwt_user"),
                email=payload.get("email", "")
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    # Fallback to test user for development
    return User(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        username="testuser",
        email="test@example.com"
    )
