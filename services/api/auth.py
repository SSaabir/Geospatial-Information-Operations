from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Dict, Any, Generator, Optional
import random
import logging

from models.user import (
    UserDB, UserCreate, UserLogin, UserResponse, UserUpdate, 
    ChangePassword, Token, RefreshToken
)
from security.jwt_handler import (
    jwt_handler, verify_password, get_password_hash, 
    create_tokens_for_user, refresh_access_token
)
from security.auth_middleware import get_current_user, get_optional_user, security
from db_config import DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Database configuration
db_config = DatabaseConfig()

# Temporary in-memory email verification store
email_verification_codes = {}

def get_db() -> Generator[Session, None, None]:
    """Get database session (generator for FastAPI Depends)"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# ------------------ EMAIL VERIFICATION ADDITIONS ------------------ #

class VerificationRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

@auth_router.post("/send-verification-code")
async def send_verification_code(request: VerificationRequest, background_tasks: BackgroundTasks):
    """
    Send a 6-digit verification code to user's email.
    """
    try:
        code = str(random.randint(100000, 999999))
        email_verification_codes[request.email] = code
        logger.info(f"Verification code for {request.email}: {code}")

        # Simulate sending email in background
        background_tasks.add_task(
            lambda: logger.info(f"Simulated email sent to {request.email} with code {code}")
        )

        return {"message": f"Verification code sent to {request.email}"}
    except Exception as e:
        logger.error(f"Error sending verification code: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification code")

@auth_router.post("/verify-email")
async def verify_email_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    """
    Verify email using a 6-digit code.
    """
    try:
        stored_code = email_verification_codes.get(request.email)
        if not stored_code or stored_code != request.code:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")

        # Mark user email as verified if exists
        user = db.query(UserDB).filter(UserDB.email == request.email).first()
        if user:
            if hasattr(user, "email_verified"):
                user.email_verified = True
                db.commit()

        email_verification_codes.pop(request.email, None)
        return {"message": "Email successfully verified"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")

# ------------------------------------------------------------------ #

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        existing_user = db.query(UserDB).filter(
            (UserDB.username == user_data.username) | 
            (UserDB.email == user_data.email)
        ).first()
        if existing_user:
            detail = "Username already exists" if existing_user.username == user_data.username else "Email already exists"
            raise HTTPException(status_code=400, detail=detail)

        # Ensure email verified before registration (optional)
        verified_code = email_verification_codes.get(user_data.email)
        if not verified_code:
            raise HTTPException(status_code=400, detail="Please verify your email before registration")

        hashed_password = get_password_hash(user_data.password)
        new_user = UserDB(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.username}",
            tier=user_data.tier or "free",
            email_verified=True if hasattr(UserDB, "email_verified") else None
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"New user registered: {new_user.username}")
        return UserResponse.from_orm(new_user)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error: {e}")
        raise HTTPException(status_code=400, detail="User registration failed due to data conflict")
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

# ------------------------------------------------------------------ #
# ALL OTHER ORIGINAL ROUTES BELOW ARE UNCHANGED
# ------------------------------------------------------------------ #

@auth_router.post("/login", response_model=Dict[str, Any])
async def login_user(user_credentials: UserLogin, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        user = db.query(UserDB).filter(
            (UserDB.username == user_credentials.username) | 
            (UserDB.email == user_credentials.username)
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")

        if not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user.last_login = datetime.now(timezone.utc)
        db.commit()

        tokens = create_tokens_for_user({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tier": getattr(user, "tier", "free")
        })

        response_data = {**tokens, "user": UserResponse.from_orm(user).dict()}
        logger.info(f"User logged in: {user.username}")
        return response_data
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@auth_router.post("/logout")
async def logout_user(current_user: UserDB = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        if hasattr(jwt_handler, 'blacklist_token'):
            jwt_handler.blacklist_token(token)
        logger.info(f"User logged out: {current_user.username}")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken):
    try:
        new_tokens = refresh_access_token(refresh_data.refresh_token)
        if not new_tokens:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return new_tokens
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

class TierChangeRequest(BaseModel):
    tier: str = Field(..., description="New tier: free, researcher, professional")

@auth_router.post("/me/tier", response_model=UserResponse)
async def change_user_tier(request: TierChangeRequest, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        allowed_tiers = {"free", "researcher", "professional"}
        new_tier = request.tier.strip().lower()
        if new_tier not in allowed_tiers:
            raise HTTPException(status_code=400, detail="Invalid tier")

        if getattr(current_user, "tier", "free") == new_tier:
            return UserResponse.from_orm(current_user)

        current_user.tier = new_tier
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        return UserResponse.from_orm(current_user)
    except Exception as e:
        db.rollback()
        logger.error(f"Change tier error: {e}")
        raise HTTPException(status_code=500, detail="Failed to change tier")

# ✅ UPDATED FUNCTION BELOW (for settings page)
@auth_router.put("/me", response_model=UserResponse)
async def update_current_user(user_update: UserUpdate, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Allow updating username (with uniqueness check)
        if getattr(user_update, "username", None) is not None:
            existing_user = db.query(UserDB).filter(
                UserDB.username == user_update.username,
                UserDB.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already exists")
            current_user.username = user_update.username

        # Update full name if provided
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name

        # Update email (and force re-verification if you track that)
        if user_update.email is not None:
            existing_user = db.query(UserDB).filter(
                UserDB.email == user_update.email,
                UserDB.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already exists")

            # Force re-verification if email changed
            current_user.email = user_update.email
            if hasattr(current_user, "email_verified"):
                current_user.email_verified = False

        # Update avatar URL if provided
        if user_update.avatar_url is not None:
            current_user.avatar_url = user_update.avatar_url

        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        return UserResponse.from_orm(current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"User update error: {e}")
        raise HTTPException(status_code=500, detail="User update failed")

@auth_router.post("/change-password")
async def change_password(password_data: ChangePassword, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")

        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Password changed successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Password change failed")

@auth_router.get("/verify-token")
async def verify_token_endpoint(current_user: UserDB = Depends(get_current_user)):
    return {"valid": True, "user_id": current_user.id, "username": current_user.username}
