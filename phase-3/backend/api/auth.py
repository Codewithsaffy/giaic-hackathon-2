from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import uuid

from auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user info from JWT token.
    This endpoint verifies the JWT and returns user information.
    """
    # Extract user info from the token payload
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )

    return {
        "id": user_id,
        "email": current_user.get("email", ""),
        "name": current_user.get("name", ""),
        "created_at": current_user.get("iat")
    }