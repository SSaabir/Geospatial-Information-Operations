"""
News API
Endpoints for fetching and managing news articles
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Generator
from db_config import DatabaseConfig
from models.news import NewsArticleDB, NewsArticleResponse, NewsFeedResponse
from models.user import UserDB
from security.auth_middleware import get_current_user
from agents.news_collector import NewsCollectorAgent
import logging

logger = logging.getLogger(__name__)

news_router = APIRouter(prefix="/api/news", tags=["News"])

# Database configuration
db_config = DatabaseConfig()

def get_db() -> Generator[Session, None, None]:
    """Get database session (generator for FastAPI Depends)"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

@news_router.get("/feed", response_model=NewsFeedResponse)
async def get_news_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category: weather, climate, environmental"),
    db: Session = Depends(get_db)
):
    """
    Get paginated news feed
    
    **Public endpoint** - No authentication required
    """
    try:
        # Build query
        query = db.query(NewsArticleDB).filter(NewsArticleDB.is_active == True)
        
        if category:
            query = query.filter(NewsArticleDB.category == category)
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * page_size
        articles = query.order_by(NewsArticleDB.published_at.desc()).offset(offset).limit(page_size).all()
        
        return NewsFeedResponse(
            total=total,
            page=page,
            page_size=page_size,
            articles=articles
        )
        
    except Exception as e:
        logger.error(f"Error fetching news feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news feed")

@news_router.get("/alerts", response_model=List[NewsArticleResponse])
async def get_news_alerts(
    threshold: int = Query(70, ge=0, le=100, description="Minimum relevance score"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get high-relevance news alerts for dashboard
    
    **Requires authentication**
    
    Returns recent, high-relevance articles (last 3 days, score >= threshold)
    """
    try:
        collector = NewsCollectorAgent(db)
        alerts = collector.get_relevant_alerts(threshold=threshold)
        return alerts[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching news alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news alerts")

@news_router.get("/{article_id}", response_model=NewsArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific news article by ID
    
    **Public endpoint**
    """
    article = db.query(NewsArticleDB).filter(NewsArticleDB.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article

@news_router.post("/collect")
async def collect_news(
    days_back: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    max_articles: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Manually trigger news collection
    
    **Admin only endpoint**
    
    Collects news from external sources and stores in database
    """
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        collector = NewsCollectorAgent(db)
        result = collector.collect_news(days_back=days_back, max_articles=max_articles)
        
        return {
            "success": result["success"],
            "message": f"Collected {result['collected']} new articles, skipped {result['skipped']} existing",
            "collected": result["collected"],
            "skipped": result["skipped"]
        }
        
    except Exception as e:
        logger.error(f"Error triggering news collection: {e}")
        raise HTTPException(status_code=500, detail=f"News collection failed: {str(e)}")

@news_router.get("/stats/summary")
async def get_news_stats(
    db: Session = Depends(get_db)
):
    """
    Get news collection statistics
    
    **Public endpoint**
    """
    try:
        total_articles = db.query(NewsArticleDB).filter(NewsArticleDB.is_active == True).count()
        weather_count = db.query(NewsArticleDB).filter(
            NewsArticleDB.category == "weather",
            NewsArticleDB.is_active == True
        ).count()
        climate_count = db.query(NewsArticleDB).filter(
            NewsArticleDB.category == "climate",
            NewsArticleDB.is_active == True
        ).count()
        environmental_count = db.query(NewsArticleDB).filter(
            NewsArticleDB.category == "environmental",
            NewsArticleDB.is_active == True
        ).count()
        
        return {
            "total_articles": total_articles,
            "by_category": {
                "weather": weather_count,
                "climate": climate_count,
                "environmental": environmental_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching news stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news statistics")
