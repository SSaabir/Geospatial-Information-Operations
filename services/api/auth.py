from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from pydantic import BaseModel, Field
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

# ---------------------------
# Logging Config
# ---------------------------
logger = logging.getLogger(__name__)

# ---------------------------
# Router
# ---------------------------
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------
# Database Session
# ---------------------------
db_config = DatabaseConfig()

def get_db() -> Generator[Session, None, None]:
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Register
# ---------------------------
@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        existing_user = db.query(UserDB).filter(
            (UserDB.username == user_data.username) | (UserDB.email == user_data.email)
        ).first()
        if existing_user:
            detail = "Username already exists" if existing_user.username == user_data.username else "Email already exists"
            raise HTTPException(status_code=400, detail=detail)

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
        return UserResponse.from_orm(new_user)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during registration: {e}")
        raise HTTPException(status_code=400, detail="Registration failed: data conflict")
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

# ---------------------------
# Login (Email only)
# ---------------------------
@auth_router.post("/login", response_model=Dict[str, Any])
async def login_user(user_credentials: UserLogin, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        user = db.query(UserDB).filter(UserDB.email == user_credentials.email).first()
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")

        user.last_login = datetime.now(timezone.utc)
        db.commit()

        tokens = create_tokens_for_user({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tier": getattr(user, "tier", "free")
        })

        return {**tokens, "user": UserResponse.from_orm(user).dict()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

# ---------------------------
# Logout
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
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

# ---------------------------
# Token Refresh
# ---------------------------
@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken):
    try:
        new_tokens = refresh_access_token(refresh_data.refresh_token)
        if not new_tokens:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return new_tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

# ---------------------------
# Get Current User (Profile)
# ---------------------------
@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

# ---------------------------
# Update Current User (Profile Edit)
# ---------------------------
class ProfileUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    tier: str | None = Field(None, description="free / researcher / professional")

@auth_router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: ProfileUpdate,
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
                raise HTTPException(status_code=400, detail="Email already exists")
            current_user.email = user_update.email

        if user_update.tier is not None:
            allowed_tiers = {"free", "researcher", "professional"}
            new_tier = user_update.tier.strip().lower()
            if new_tier not in allowed_tiers:
                raise HTTPException(status_code=400, detail="Invalid tier")
            current_user.tier = new_tier

        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
        logger.info(f"User profile updated: {current_user.username}")
        return UserResponse.from_orm(current_user)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"User update error: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")

# ---------------------------

