from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
from sqlalchemy.orm import Session

from security.jwt_handler import jwt_handler, JWTHandler
from models.user import UserDB, TokenData
from db_config import DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()

# Database configuration instance
db_config = DatabaseConfig()

# Dependency functions for FastAPI
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> Dict[str, Any]:
    """
    Verify JWT token dependency with auto-refresh capability
    
    Args:
        credentials: HTTP Bearer credentials
        request: FastAPI request object for setting refresh header
        
    Returns:
        Dict[str, Any]: Token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Verify token with auto-refresh enabled
    payload = jwt_handler.verify_token(token, "access", auto_refresh=True)
    if payload is None:
        # Try to extract refresh token from cookie or header
        refresh_token = None
        if request:
            refresh_token = request.cookies.get("refresh_token") or request.headers.get("X-Refresh-Token")
        
        if refresh_token:
            # Attempt to refresh using the refresh token
            new_tokens = jwt_handler.refresh_access_token(refresh_token)
            if new_tokens:
                # Return new payload with refresh header
                new_payload = jwt_handler.verify_token(new_tokens["access_token"], "access")
                if new_payload:
                    # Set the new access token in response header
                    if request:
                        request.state.new_access_token = new_tokens["access_token"]
                    return new_payload
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserDB:
    """Get current user dependency"""
    token_data = await verify_token(credentials)
    username = token_data.get("sub")
    user_id = token_data.get("user_id")
    
    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get database session
    db = db_config.get_session()
    try:
        # Find user in database
        user = db.query(UserDB).filter(
            UserDB.id == user_id,
            UserDB.username == username
        ).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return user
        
    finally:
        db.close()

async def get_current_admin_user(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    """Get current admin user dependency"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserDB]:
    """Optional authentication dependency"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt_handler.verify_token(token, "access")
        
        if payload is None:
            return None
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if username is None or user_id is None:
            return None
        
        # Get database session
        db = db_config.get_session()
        try:
            user = db.query(UserDB).filter(
                UserDB.id == user_id,
                UserDB.username == username,
                UserDB.is_active == True
            ).first()
            
            return user
            
        finally:
            db.close()
            
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None

# Custom exception handlers
class AuthenticationError(Exception):
    """Custom authentication error"""
    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Custom authorization error"""
    def __init__(self, message: str, status_code: int = status.HTTP_403_FORBIDDEN):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)