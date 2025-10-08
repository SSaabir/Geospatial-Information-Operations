
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
from middleware.event_logger import log_auth_event, increment_usage_metrics
from services.utils.notification_manager import notify

# Configure logging
logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Database configuration
db_config = DatabaseConfig()

def get_db() -> Generator[Session, None, None]:
    """Get database session (generator for FastAPI Depends)

    Returns a generator yielding a SQLAlchemy Session.
    """
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Validate password confirmation
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if username already exists
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
        
        # Create new user
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
            # Log auth event (best-effort)
            log_auth_event("register", new_user.id, True)
            increment_usage_metrics(new_user.id, api_calls=1)
        except Exception as e:
            logger.exception("Non-fatal: failed to log auth event during register: %s", e)
        # Send welcome/registration notification (non-blocking best-effort)
        try:
            notify(
                subject="New user registered",
                message=f"User {new_user.username} (id={new_user.id}) registered.",
                level="info",
                metadata={"user_id": new_user.id, "username": new_user.username}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send registration notification")
        return UserResponse.from_orm(new_user)
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during registration: {e}")
        # Notify admin about failed registration due to integrity conflict
        try:
            notify(
                subject="Registration failed - data conflict",
                message=f"A registration attempt failed due to data conflict: {str(e)}",
                level="critical",
                metadata={"error": str(e)}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send registration failure notification")
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

@auth_router.post("/login", response_model=Dict[str, Any])
async def login_user(
    user_credentials: UserLogin, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    
    Args:
        user_credentials: User login credentials
        background_tasks: Background tasks for async operations
        db: Database session
        
    Returns:
        Dict: JWT tokens and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Find user by username or email
        user = db.query(UserDB).filter(
            (UserDB.username == user_credentials.username) | 
            (UserDB.email == user_credentials.username)
        ).first()
        
        if not user:
            # Notify about failed login attempt (unknown user) and return
            try:
                background_tasks.add_task(
                    notify,
                    subject="Failed login attempt - unknown user",
                    message=f"Login attempt for unknown user identifier: {user_credentials.username}",
                    level="warning",
                    metadata={"username": user_credentials.username}
                )
            except Exception:
                logger.exception("Non-fatal: failed to enqueue failed-login notification")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user.hashed_password):
            # Notify about failed login attempt (invalid password)
            try:
                background_tasks.add_task(
                    notify,
                    subject="Failed login attempt - invalid password",
                    message=f"Invalid password for user {user.username} (id={user.id}) from request identifier: {user_credentials.username}",
                    level="warning",
                    metadata={"user_id": user.id, "username": user.username}
                )
            except Exception:
                logger.exception("Non-fatal: failed to enqueue failed-login notification")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Create tokens
        tokens = create_tokens_for_user({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "tier": getattr(user, "tier", "free")
        })
        
        # Prepare response
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
        # Non-blocking notification for successful login (optional, keep light)
        try:
            background_tasks.add_task(
                notify,
                subject="User logged in",
                message=f"User {user.username} (id={user.id}) logged in.",
                level="info",
                metadata={"user_id": user.id, "username": user.username}
            )
        except Exception:
            logger.exception("Non-fatal: failed to enqueue login notification")

        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@auth_router.post("/logout")
async def logout_user(
    current_user: UserDB = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user by blacklisting the current token
    
    Args:
        current_user: Currently authenticated user
        credentials: Current JWT token credentials
        
    Returns:
        Dict: Logout confirmation
    """
    try:
        # Get token from authorization header
        token = credentials.credentials
        
        # Blacklist the token
        if hasattr(jwt_handler, 'blacklist_token'):
            jwt_handler.blacklist_token(token)
        
        logger.info(f"User logged out: {current_user.username}")
        try:
            log_auth_event("logout", current_user.id, True)
        except Exception as e:
            logger.exception("Non-fatal: failed to log auth event during logout: %s", e)
        # Best-effort notification about logout
        try:
            notify(
                subject="User logged out",
                message=f"User {current_user.username} (id={current_user.id}) logged out.",
                level="info",
                metadata={"user_id": current_user.id, "username": current_user.username}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send logout notification")
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshToken):
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token data
        
    Returns:
        Token: New access token
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        new_tokens = refresh_access_token(refresh_data.refresh_token)
        
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        # Non-PII token refresh notification (does not include token)
        try:
            notify(
                subject="Access token refreshed",
                message="A user refreshed their access token successfully.",
                level="info",
                metadata={}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send token refresh notification")
        return new_tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    """
    Get current user information
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return UserResponse.from_orm(current_user)


class TierChangeRequest(BaseModel):
    """Request model to change current user's subscription tier"""
    tier: str = Field(..., description="New tier: free, researcher, professional")


@auth_router.post("/me/tier", response_model=UserResponse)
async def change_user_tier(
    request: TierChangeRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's subscription tier.

    This is a placeholder for billing integration. In production, this should be
    called only after successful payment confirmation via webhook.
    """
    try:
        allowed_tiers = {"free", "researcher", "professional"}
        new_tier = request.tier.strip().lower()
        if new_tier not in allowed_tiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tier. Must be one of: free, researcher, professional"
            )

        # No-op if tier is the same
        if getattr(current_user, "tier", "free") == new_tier:
            return UserResponse.from_orm(current_user)

        old_tier = getattr(current_user, "tier", "free")
        current_user.tier = new_tier
        current_user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)

        # Notify about tier change
        try:
            notify(
                subject="Subscription tier changed",
                message=f"User {current_user.username} (id={current_user.id}) changed tier from {old_tier} to {new_tier}.",
                level="info",
                metadata={"user_id": current_user.id, "from": old_tier, "to": new_tier}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send tier-change notification")
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

@auth_router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information
    
    Args:
        user_update: User update data
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user information
    """
    try:
        # Update user fields
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name
        
        if user_update.email is not None:
            # Check if email is already taken
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
        try:
            notify(
                subject="User profile updated",
                message=f"User {current_user.username} (id={current_user.id}) updated their profile.",
                level="info",
                metadata={"user_id": current_user.id}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send profile update notification")
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

@auth_router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Args:
        password_data: Password change data
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        Dict: Success message
    """
    try:
        # Validate password confirmation
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        try:
            notify(
                subject="Password changed",
                message=f"Password changed for user {current_user.username} (id={current_user.id}).",
                level="warning",
                metadata={"user_id": current_user.id}
            )
        except Exception:
            logger.exception("Non-fatal: failed to send password change notification")
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

@auth_router.get("/verify-token")
async def verify_token_endpoint(current_user: UserDB = Depends(get_current_user)):
    """
    Verify if the current token is valid
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        Dict: Token validity confirmation
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username
    }