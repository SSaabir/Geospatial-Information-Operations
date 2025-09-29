from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime

Base = declarative_base()

# SQLAlchemy ORM Model
class UserDB(Base):
    """SQLAlchemy ORM model for users table"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    avatar_url = Column(Text, nullable=True)
    


# Pydantic Models for API
class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str

class UserResponse(UserBase):
    """User response model (without sensitive data)"""
    id: int
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class ChangePassword(BaseModel):
    """Change password model"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

# Token Models
class Token(BaseModel):
    """JWT token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token payload data model"""
    username: Optional[str] = None
    user_id: Optional[int] = None

class RefreshToken(BaseModel):
    """Refresh token model"""
    refresh_token: str