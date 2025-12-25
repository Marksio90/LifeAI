"""
Extended authentication endpoints for email verification and password reset.

Add these endpoints to backend/app/api/auth.py:
"""

from datetime import datetime, timezone, timedelta


# Add these Pydantic models to auth.py:
"""
class EmailVerificationRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        \"\"\"Validate new password requirements\"\"\"
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)

        if not has_upper:
            raise ValueError('Password must contain at least one uppercase letter')
        if not has_lower:
            raise ValueError('Password must contain at least one lowercase letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        if not has_special:
            raise ValueError('Password must contain at least one special character')

        return v
"""

# Add these endpoints to auth.py router:
ENDPOINTS_TO_ADD = """

@router.post("/send-verification")
async def send_verification_email_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"
    Send verification email to user.
    User must be logged in.
    \"\"\"
    from app.services.email_service import get_email_service

    if current_user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )

    # Generate verification token
    email_service = get_email_service()
    verification_token = email_service.generate_verification_token()
    hashed_token = email_service.hash_token(verification_token)

    # Store hashed token and expiration
    current_user.verification_token = hashed_token
    current_user.verification_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    db.commit()

    # Send email
    success = email_service.send_verification_email(
        to_email=current_user.email,
        verification_token=verification_token,
        user_name=current_user.full_name
    )

    if not success:
        return {
            "success": False,
            "message": "Failed to send verification email. Email service may not be configured."
        }

    return {
        "success": True,
        "message": "Verification email sent successfully"
    }


@router.post("/verify-email")
async def verify_email(
    data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    \"\"\"
    Verify user email with token from email.
    \"\"\"
    from app.services.email_service import get_email_service

    email_service = get_email_service()
    hashed_token = email_service.hash_token(data.token)

    # Find user with this token
    user = db.query(User).filter(
        User.verification_token == hashed_token
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )

    # Check if token is expired
    if user.verification_token_expires and user.verification_token_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Verification token has expired. Please request a new one."
        )

    # Mark as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "message": "Email verified successfully"
    }


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    _: None = Depends(login_limiter)
):
    \"\"\"
    Request password reset email.
    Rate limited to prevent abuse.
    \"\"\"
    from app.services.email_service import get_email_service

    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return {
            "success": True,
            "message": "If that email exists, a password reset link has been sent."
        }

    # Generate reset token
    email_service = get_email_service()
    reset_token = email_service.generate_password_reset_token()
    hashed_token = email_service.hash_token(reset_token)

    # Store hashed token and expiration (1 hour)
    user.password_reset_token = hashed_token
    user.password_reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    # Send email
    email_service.send_password_reset_email(
        to_email=user.email,
        reset_token=reset_token,
        user_name=user.full_name
    )

    return {
        "success": True,
        "message": "If that email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
    _: None = Depends(login_limiter)
):
    \"\"\"
    Reset password using token from email.
    \"\"\"
    from app.services.email_service import get_email_service

    email_service = get_email_service()
    hashed_token = email_service.hash_token(data.token)

    # Find user with this token
    user = db.query(User).filter(
        User.password_reset_token == hashed_token
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    # Check if token is expired
    if user.password_reset_token_expires and user.password_reset_token_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired. Please request a new one."
        )

    # Update password
    user.password_hash = get_password_hash(data.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "message": "Password reset successfully. You can now login with your new password."
    }
"""

print("Add the following models and endpoints to backend/app/api/auth.py")
print("\n=== MODELS ===")
print("Add after existing Pydantic models (around line 168):")
print("""
class EmailVerificationRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)

        if not has_upper:
            raise ValueError('Password must contain at least one uppercase letter')
        if not has_lower:
            raise ValueError('Password must contain at least one lowercase letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        if not has_special:
            raise ValueError('Password must contain at least one special character')

        return v
""")

print("\n=== ENDPOINTS ===")
print("Add at the end of the file (after change-password endpoint):")
print(ENDPOINTS_TO_ADD)

print("\n=== DATABASE MIGRATION ===")
print("Add to User model (backend/app/models/user.py):")
print("""
    # Email verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)
""")
