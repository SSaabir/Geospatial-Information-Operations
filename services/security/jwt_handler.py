"""
JWT Token Handler for Authentication

This module handles JWT token creation, validation, and management for the authentication system.
It provides secure token generation with proper expiration and refresh token functionality.

Author: Saabir
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt as jose_jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import redis
import json
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Redis configuration for token blacklisting (optional)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

class JWTHandler:
    """JWT token handler for authentication operations"""
    
    def __init__(self):
        """Initialize JWT handler with Redis connection for token blacklisting"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                decode_responses=True
            )
            # Test Redis connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis connection established for token blacklisting")
        except Exception as e:
            logger.warning(f"Redis not available, token blacklisting disabled: {e}")
            self.redis_client = None
            self.redis_available = False
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jose_jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Token payload data
            
        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        encoded_jwt = jose_jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
            token_type: Expected token type (access or refresh)
            
        Returns:
            Dict containing token payload or None if invalid
        """
        try:
            # Check if token is blacklisted
            if self.is_token_blacklisted(token):
                logger.warning("Attempted to use blacklisted token")
                return None
            
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch. Expected {token_type}, got {payload.get('type')}")
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist
        
        Args:
            token: JWT token to blacklist
            
        Returns:
            bool: True if successfully blacklisted
        """
        if not self.redis_available:
            logger.warning("Redis not available, cannot blacklist token")
            return False
        
        try:
            # Decode token to get expiration
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            exp = payload.get("exp")
            
            if exp:
                # Calculate TTL (time to live) until token expires
                expire_time = datetime.fromtimestamp(exp, timezone.utc)
                ttl = max(0, int((expire_time - datetime.now(timezone.utc)).total_seconds()))
                
                # Store token hash in Redis with TTL
                token_hash = self._hash_token(token)
                self.redis_client.setex(f"blacklist:{token_hash}", ttl, "1")
                
                logger.info("Token successfully blacklisted")
                return True
            
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
        
        return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted
        
        Args:
            token: JWT token to check
            
        Returns:
            bool: True if token is blacklisted
        """
        if not self.redis_available:
            return False
        
        try:
            token_hash = self._hash_token(token)
            return self.redis_client.exists(f"blacklist:{token_hash}") > 0
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
    
    def _hash_token(self, token: str) -> str:
        """
        Create hash of token for blacklisting
        
        Args:
            token: JWT token to hash
            
        Returns:
            str: Token hash
        """
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()
    


# Global JWT handler instance
jwt_handler = JWTHandler()

# Helper functions for password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

# Token creation helper functions
def create_tokens_for_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create access and refresh tokens for user
    
    Args:
        user_data: User information to encode in token
        
    Returns:
        Dict containing both tokens and metadata
    """
    access_token = jwt_handler.create_access_token(
        data={"sub": user_data["username"], "user_id": user_data["id"]}
    )
    
    refresh_token = jwt_handler.create_refresh_token(
        data={"sub": user_data["username"], "user_id": user_data["id"]}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }

def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    Create new access token from refresh token
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        Dict with new access token or None if invalid
    """
    payload = jwt_handler.verify_token(refresh_token, "refresh")
    if not payload:
        return None
    
    # Create new access token
    access_token = jwt_handler.create_access_token(
        data={"sub": payload["sub"], "user_id": payload["user_id"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }