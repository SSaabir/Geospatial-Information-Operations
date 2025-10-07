from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from typing import Dict, Any, Generator
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

def get_db() -> Generator[Session, None, None]:
    """Get database session (generator for FastAPI Depends)"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Register user
# ---------------------------
@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )

        existing_user = db.query(UserDB).filter(
            (UserDB.username == user_data.username) |
            (UserDB.email == user_data.email)
        ).first()
        
        if existing_user:
            detail = "Username already exists" if existing_user.username == user_data.username else "Email already exists"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
        
        hashed_password = get_password_hash(user_data.password)
        new_user = UserDB(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.username}",
            tier=user_data.tier or "free"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.username}")
        try:
            log_auth_event("register", new_user.id, True)
            increment_usage_metrics(new_user.id, api_calls=1)
        except Exception as e:
            logger.exception("Non-fatal: failed to log auth event during register: %s", e)
        return UserResponse.from_orm(new_user)
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed due to data conflict"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

# ---------------------------
# Login user (email only)
# ---------------------------
@auth_router.post("/login", response_model=Dict[str, Any])
async def login_user(
    user_credentials: UserLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        # Login with email
        user = db.query(UserDB).filter(
            UserDB.email == user_credentials.email
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        if not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        tokens = create_tokens_for_user({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tier": getattr(user, "tier", "free")
        })
        
        response_data = {
            **tokens,
            "user": UserResponse.from_orm(user).dict()
        }
        
        logger.info(f"User logged in: {user.username}")
        try:
            log_auth_event("login", user.id, True)
            increment_usage_metrics(user.id, api_calls=1)
        except Exception as e:
            logger.exception("Non-fatal: failed to log auth event during login: %s", e)
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# ---------------------------
# Logout user
# ---------------------------
@auth_router.post("/logout")
async def logout_user(
    current_user: UserDB = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        if hasattr(jwt_handler, 'blacklist_token'):
            jwt_handler.blacklist_token(token)
        logger.info(f"User logged out: {current_user.username}")
        try:
            log_auth_event("logout", current_user.id, True)
        except Exception as e:
            logger.exception("Non-fatal: failed to log auth event during logout: %s", e)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# ---------------------------
# Token refresh
# ---------------------------
@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken):
    try:
        new_tokens = refresh_access_token(refresh_data.refresh_token)
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        return new_tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

# ---------------------------
# Current user info
# ---------------------------
@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

class TierChangeRequest(BaseModel):
    tier: str = Field(..., description="New tier: free, researcher, professional")

@auth_router.post("/me/tier", response_model=UserResponse)
async def change_user_tier(
    request: TierChangeRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        allowed_tiers = {"free", "researcher", "professional"}
        new_tier = request.tier.strip().lower()
        if new_tier not in allowed_tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tier. Must be one of: free, researcher, professional"
            )
        if getattr(current_user, "tier", "free") == new_tier:
            return UserResponse.from_orm(current_user)
        current_user.tier = new_tier
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        return UserResponse.from_orm(current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Change tier error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change tier"
        )

# ---------------------------
# Update current user
# ---------------------------
@auth_router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name
        if user_update.email is not None:
            existing_user = db.query(UserDB).filter(
                UserDB.email == user_update.email,
                UserDB.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            current_user.email = user_update.email
        if user_update.avatar_url is not None:
            current_user.avatar_url = user_update.avatar_url
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        logger.info(f"User updated: {current_user.username}")
        return UserResponse.from_orm(current_user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"User update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

# ---------------------------
# Change password
# ---------------------------
@auth_router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Password changed for user: {current_user.username}")
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

# ---------------------------
# Verify token
# ---------------------------
@auth_router.get("/verify-token")
async def verify_token_endpoint(current_user: UserDB = Depends(get_current_user)):
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }
