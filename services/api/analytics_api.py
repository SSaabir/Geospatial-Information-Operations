from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session

from security.auth_middleware import get_current_user
from models.user import UserDB
from models.usage import UsageMetrics
from db_config import DatabaseConfig

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


@analytics_router.get("/usage", response_model=Dict[str, Any])
async def get_usage(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    metrics = db.query(UsageMetrics).filter(UsageMetrics.user_id == current_user.id).first()
    if not metrics:
        metrics = UsageMetrics(user_id=current_user.id)
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
    
    # Calculate limits and remaining usage
    tier = getattr(current_user, "tier", "free")
    tier_limits = {"free": 5, "researcher": 5000, "professional": float('inf')}
    limit = tier_limits.get(tier, 5)
    remaining = max(0, limit - metrics.api_calls) if limit != float('inf') else float('inf')
    
    return {
        "api_calls": metrics.api_calls,
        "reports_generated": metrics.reports_generated,
        "data_downloads": metrics.data_downloads,
        "limit": limit,
        "remaining": remaining,
        "tier": tier
    }


