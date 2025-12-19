from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.security.auth import get_current_user, get_current_premium_user


async def require_auth(current_user: User = Depends(get_current_user)) -> User:
    """Require authenticated user"""
    return current_user


async def require_premium(current_user: User = Depends(get_current_premium_user)) -> User:
    """Require premium subscription"""
    return current_user
