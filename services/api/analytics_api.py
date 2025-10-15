from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import timedelta
import os
import logging
from sqlalchemy.orm import Session

from security.auth_middleware import get_current_user
from models.user import UserDB
from models.usage import UsageMetrics
from db_config import DatabaseConfig
from utils.notification_manager import notify

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

db_config = DatabaseConfig()
logger = logging.getLogger(__name__)

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


@analytics_router.get("/usage", response_model=Dict[str, Any])
async def get_usage(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get usage statistics - READ-ONLY operation, does not count toward quota.
    This endpoint is for displaying usage info, not consuming API calls.
    """
    tier = getattr(current_user, "tier", "free")
    
    # Get or create usage metrics (READ-ONLY - no increment)
    metrics = db.query(UsageMetrics).filter(UsageMetrics.user_id == current_user.id).first()
    if not metrics:
        metrics = UsageMetrics(user_id=current_user.id)
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
    
    # Calculate limits and remaining usage
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


# --- Event models and endpoints for analytics notifications ---

class AnalyticsEvent(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    duration_ms: Optional[int] = Field(None, description="Execution duration in milliseconds")
    query_summary: Optional[str] = Field(None, description="Short description of the query/job")
    error: Optional[str] = Field(None, description="Error message if the job failed")
    anomalous: Optional[bool] = Field(False, description="Whether the result was anomalous")


def _get_long_query_threshold_ms() -> int:
    try:
        return int(os.getenv("ANALYTICS_LONG_QUERY_MS", "5000"))
    except Exception:
        return 5000


@analytics_router.post("/events")
async def report_analytics_event(
    event: AnalyticsEvent,
    current_user: UserDB = Depends(get_current_user)
):
    """Report analytics job outcome and trigger notifications.

    Triggers:
    - long-running query (> threshold): warning
    - job failure: critical
    - anomalous result: warning

    Channels:
    - user email (if authenticated user present)
    - admin webhook (GLOBAL_WEBHOOK_URL)
    - DB storage (via notification manager if DB is configured)
    """
    metadata = {
        "job_id": event.job_id,
        "duration": event.duration_ms,
        "query_summary": event.query_summary,
        "error": event.error,
        "user_id": getattr(current_user, "id", None),
    }

    threshold = _get_long_query_threshold_ms()

    try:
        # Job failure
        if event.error:
            notify(
                subject="Analytics job failed",
                message=f"Job {event.job_id} failed: {event.error}",
                level="critical",
                to_email=current_user.email if getattr(current_user, "email", None) else None,
                metadata=metadata,
            )

        # Long-running query
        if event.duration_ms is not None and event.duration_ms > threshold:
            dur_s = round(event.duration_ms / 1000.0, 2)
            notify(
                subject="Long-running analytics query",
                message=f"Job {event.job_id} exceeded threshold ({dur_s}s > {threshold}ms).",
                level="warning",
                to_email=current_user.email if getattr(current_user, "email", None) else None,
                metadata=metadata,
            )

        # Anomalous result
        if event.anomalous:
            notify(
                subject="Anomalous analytics result detected",
                message=f"Job {event.job_id} produced an anomalous result.",
                level="warning",
                to_email=current_user.email if getattr(current_user, "email", None) else None,
                metadata=metadata,
            )
    except Exception as e:
        logger.exception("Failed to send analytics event notification: %s", e)
        raise HTTPException(status_code=500, detail="Failed to process analytics event")

    return {"status": "ok"}

