"""
Dashboard API - Provides user-specific dashboard data and statistics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import os

from security.auth_middleware import get_current_user
from models.user import UserDB
from models.usage import UsageMetrics
from db_config import DatabaseConfig

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
db_config = DatabaseConfig()

def get_db():
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


@dashboard_router.get("/stats")
async def get_dashboard_stats(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard statistics for the user"""
    try:
        user_id = current_user.id
        tier = getattr(current_user, "tier", "free")
        
        # Get usage metrics (READ-ONLY - does not count toward quota)
        usage = db.query(UsageMetrics).filter(UsageMetrics.user_id == user_id).first()
        if not usage:
            usage = UsageMetrics(user_id=user_id)
            db.add(usage)
            db.commit()
            db.refresh(usage)
        
        # Get tier limits
        tier = getattr(current_user, "tier", "free")
        tier_limits = {
            "free": {"api_calls": 100, "reports": 5, "downloads": 10},
            "researcher": {"api_calls": 5000, "reports": 100, "downloads": 500},
            "professional": {"api_calls": float('inf'), "reports": float('inf'), "downloads": float('inf')}
        }
        limits = tier_limits.get(tier, tier_limits["free"])
        
        # Get notification stats
        notif_query = text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN read = false THEN 1 ELSE 0 END) as unread,
                SUM(CASE WHEN level = 'warning' OR level = 'error' OR level = 'critical' THEN 1 ELSE 0 END) as alerts
            FROM notifications 
            WHERE user_id = :user_id
        """)
        notif_result = db.execute(notif_query, {"user_id": user_id}).fetchone()
        
        # Get recent activity count (last 7 days)
        recent_activity_query = text("""
            SELECT COUNT(*) as count
            FROM notifications 
            WHERE user_id = :user_id 
            AND timestamp >= :since
        """)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_activity = db.execute(
            recent_activity_query, 
            {"user_id": user_id, "since": seven_days_ago}
        ).fetchone()
        
        # Account info
        days_active = (datetime.now() - current_user.created_at).days if current_user.created_at else 0
        
        return {
            "user": {
                "name": current_user.full_name or current_user.username,
                "email": current_user.email,
                "tier": tier,
                "joined_date": current_user.created_at.isoformat() if current_user.created_at else None,
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
                "days_active": days_active,
                "is_admin": current_user.is_admin
            },
            "usage": {
                "api_calls": usage.api_calls,
                "reports_generated": usage.reports_generated,
                "data_downloads": usage.data_downloads,
                "limits": {
                    "api_calls": limits["api_calls"] if limits["api_calls"] != float('inf') else "unlimited",
                    "reports": limits["reports"] if limits["reports"] != float('inf') else "unlimited",
                    "downloads": limits["downloads"] if limits["downloads"] != float('inf') else "unlimited"
                },
                "remaining": {
                    "api_calls": max(0, limits["api_calls"] - usage.api_calls) if limits["api_calls"] != float('inf') else "unlimited",
                    "reports": max(0, limits["reports"] - usage.reports_generated) if limits["reports"] != float('inf') else "unlimited",
                    "downloads": max(0, limits["downloads"] - usage.data_downloads) if limits["downloads"] != float('inf') else "unlimited"
                }
            },
            "notifications": {
                "total": int(notif_result[0]) if notif_result else 0,
                "unread": int(notif_result[1]) if notif_result and notif_result[1] else 0,
                "alerts": int(notif_result[2]) if notif_result and notif_result[2] else 0
            },
            "activity": {
                "recent_count": int(recent_activity[0]) if recent_activity else 0,
                "last_7_days": int(recent_activity[0]) if recent_activity else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@dashboard_router.get("/weather/current")
async def get_current_weather(
    current_user: UserDB = Depends(get_current_user)
):
    """Get current weather data from historical dataset"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "history_colombo.csv")
        
        if not os.path.exists(csv_path):
            # Return mock data if CSV not found
            return {
                "temperature": 28.5,
                "humidity": 75,
                "wind_speed": 12,
                "pressure": 1013,
                "conditions": "Partly Cloudy",
                "location": "Colombo"
            }
        
        # Read the last few rows of data
        df = pd.read_csv(csv_path)
        if len(df) > 0:
            latest = df.iloc[-1]
            return {
                "temperature": float(latest.get('temperature', 28.5)),
                "humidity": float(latest.get('humidity', 75)),
                "wind_speed": float(latest.get('windspeed', 12)),
                "pressure": float(latest.get('pressure', 1013)),
                "conditions": str(latest.get('conditions', 'Clear')),
                "location": "Colombo"
            }
        else:
            raise HTTPException(status_code=404, detail="No weather data available")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@dashboard_router.get("/weather/trends")
async def get_weather_trends(
    current_user: UserDB = Depends(get_current_user),
    days: int = 7
):
    """Get weather trends for the specified number of days"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "history_colombo.csv")
        
        if not os.path.exists(csv_path):
            # Return mock trend data
            return {
                "daily_temps": [
                    {"date": "2025-10-08", "temp": 28, "humidity": 76},
                    {"date": "2025-10-09", "temp": 29, "humidity": 74},
                    {"date": "2025-10-10", "temp": 31, "humidity": 68},
                    {"date": "2025-10-11", "temp": 30, "humidity": 70},
                    {"date": "2025-10-12", "temp": 27, "humidity": 78},
                    {"date": "2025-10-13", "temp": 28, "humidity": 75},
                    {"date": "2025-10-14", "temp": 29, "humidity": 72}
                ]
            }
        
        # Read and process data
        df = pd.read_csv(csv_path)
        
        # Get last N days of data
        if len(df) > days:
            df = df.tail(days)
        
        # Prepare trend data
        trends = []
        for idx, row in df.iterrows():
            trends.append({
                "date": str(row.get('datetime', f"Day {idx + 1}")),
                "temp": float(row.get('temperature', 28)),
                "humidity": float(row.get('humidity', 75)),
                "wind_speed": float(row.get('windspeed', 12))
            })
        
        return {"daily_temps": trends}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather trends: {str(e)}")


@dashboard_router.get("/activity/recent")
async def get_recent_activity(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get recent user activity/notifications"""
    try:
        user_id = current_user.id
        
        query = text("""
            SELECT 
                id,
                timestamp,
                level,
                subject,
                message,
                read
            FROM notifications 
            WHERE user_id = :user_id
            ORDER BY timestamp DESC
            LIMIT :limit
        """)
        
        results = db.execute(query, {"user_id": user_id, "limit": limit}).fetchall()
        
        activities = []
        for row in results:
            activities.append({
                "id": row[0],
                "timestamp": row[1].isoformat() if row[1] else None,
                "type": row[2],  # level
                "title": row[3],  # subject
                "message": row[4],
                "read": row[5]
            })
        
        return {"activities": activities}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent activity: {str(e)}")
