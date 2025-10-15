from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime
from models.user import Base

# ---------------------------
# SQLAlchemy ORM Model
# ---------------------------
class NewsArticleDB(Base):
    """SQLAlchemy ORM model for news_articles table"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(200), nullable=False)  # e.g., "BBC News", "CNN"
    author = Column(String(200), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    image_url = Column(String(1000), nullable=True)
    category = Column(String(100), default="weather")  # weather, climate, environmental
    keywords = Column(JSON, nullable=True)  # Array of keywords
    relevance_score = Column(Integer, default=0)  # 0-100 relevance score
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ---------------------------
# Pydantic Models for API
# ---------------------------
class NewsArticleBase(BaseModel):
    """Base news article model"""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    content: Optional[str] = None
    url: str = Field(..., max_length=1000)
    source: str = Field(..., max_length=200)
    author: Optional[str] = Field(None, max_length=200)
    published_at: Optional[datetime] = None
    image_url: Optional[str] = Field(None, max_length=1000)
    category: str = Field("weather", max_length=100)
    keywords: Optional[List[str]] = []
    relevance_score: int = Field(0, ge=0, le=100)

class NewsArticleCreate(NewsArticleBase):
    """News article creation model"""
    pass

class NewsArticleResponse(NewsArticleBase):
    """News article response model"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NewsArticleUpdate(BaseModel):
    """News article update model"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    content: Optional[str] = None
    relevance_score: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None

class NewsFeedResponse(BaseModel):
    """News feed response with pagination"""
    total: int
    page: int
    page_size: int
    articles: List[NewsArticleResponse]
