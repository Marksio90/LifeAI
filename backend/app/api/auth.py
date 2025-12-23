from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.security.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from app.middleware.rate_limit import login_limiter

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    preferred_language: str = "pl"

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    _: None = Depends(login_limiter)
):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        preferred_language=user_data.preferred_language
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
    _: None = Depends(login_limiter)
):
    """Login user"""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user.to_dict()


@router.put("/me")
async def update_me(
    full_name: str | None = None,
    preferred_language: str | None = None,
    preferred_voice: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if full_name is not None:
        current_user.full_name = full_name
    if preferred_language is not None:
        current_user.preferred_language = preferred_language
    if preferred_voice is not None:
        current_user.preferred_voice = preferred_voice

    db.commit()
    return current_user.to_dict()


class ProfileUpdate(BaseModel):
    """Update user profile"""
    full_name: str | None = None
    preferred_language: str | None = None
    preferred_voice: str | None = None
    preferences: dict | None = None


class PasswordChange(BaseModel):
    """Change password"""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        return v


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user.to_dict()


@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Update fields if provided
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name
        
        if profile_data.preferred_language is not None:
            current_user.preferred_language = profile_data.preferred_language
        
        if profile_data.preferred_voice is not None:
            current_user.preferred_voice = profile_data.preferred_voice
        
        if profile_data.preferences is not None:
            current_user.preferences = profile_data.preferences
        
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": current_user.to_dict()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _: None = Depends(login_limiter)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Check new password is different
        if password_data.current_password == password_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        # Update password
        current_user.password_hash = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")
