from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from ..api.auth import get_current_user
from ..models.user import User

security = HTTPBearer()



def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated admin user"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active authenticated user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user

def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current verified authenticated user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified"
        )
    return current_user

def optional_current_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    return current_user