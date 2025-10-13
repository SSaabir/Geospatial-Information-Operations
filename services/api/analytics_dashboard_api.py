"""Analytics Dashboard API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from sqlalchemy import text
from datetime import datetime, timedelta

from security.auth_middleware import get_current_user
from db_config import DatabaseConfig
from models.user import UserDB

analytics_dashboard_router = APIRouter(prefix="/analytics-dashboard", tags=["analytics-dashboard"])

def get_db():
    """Dependency to get database connection"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    return engine


@analytics_dashboard_router.get("/overview")
async def get_analytics_overview(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get analytics dashboard overview statistics"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Get total API calls
            total_api_calls = conn.execute(text("""
                SELECT COUNT(*) FROM api_access_log
            """)).scalar() or 0
            
            # Get API calls in last 24h
            api_calls_24h = conn.execute(text("""
                SELECT COUNT(*) FROM api_access_log 
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)).scalar() or 0
            
            # Get total users
            total_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
            
            # Get active users (logged in last 7 days)
            active_users_7d = conn.execute(text("""
                SELECT COUNT(*) FROM users 
                WHERE last_login > NOW() - INTERVAL '7 days'
            """)).scalar() or 0
            
            # Get reports generated (sum from usage_metrics)
            reports_generated = conn.execute(text("""
                SELECT COALESCE(SUM(reports_generated), 0) FROM usage_metrics 
                WHERE updated_at > NOW() - INTERVAL '30 days'
            """)).scalar() or 0
            
            # Get data downloads (sum from usage_metrics)
            data_downloads = conn.execute(text("""
                SELECT COALESCE(SUM(data_downloads), 0) FROM usage_metrics 
                WHERE updated_at > NOW() - INTERVAL '30 days'
            """)).scalar() or 0
            
            return {
                "overview": {
                    "total_api_calls": total_api_calls,
                    "api_calls_24h": api_calls_24h,
                    "total_users": total_users,
                    "active_users_7d": active_users_7d,
                    "reports_generated": reports_generated,
                    "data_downloads": data_downloads,
                    "avg_response_time": 245  # Placeholder in ms
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics overview: {str(e)}")


@analytics_dashboard_router.get("/api-usage")
async def get_api_usage(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    time_range: str = "24h"
):
    """Get API usage statistics over time"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        # Parse time range
        hours = 24
        interval = "hour"
        if time_range == "1h":
            hours = 1
            interval = "minute"
        elif time_range == "7d":
            hours = 168
            interval = "hour"
        elif time_range == "30d":
            hours = 720
            interval = "day"
        
        with db.connect() as conn:
            # Get API calls grouped by time
            if interval == "minute":
                result = conn.execute(text("""
                    SELECT 
                        TO_CHAR(timestamp, 'HH24:MI') as time,
                        COUNT(*) as count
                    FROM api_access_log 
                    WHERE timestamp > NOW() - INTERVAL '1 hour'
                    GROUP BY TO_CHAR(timestamp, 'HH24:MI')
                    ORDER BY time
                """))
            elif interval == "hour":
                if time_range == "24h":
                    interval_str = "24 hours"
                else:
                    interval_str = "7 days"
                result = conn.execute(text(f"""
                    SELECT 
                        TO_CHAR(timestamp, 'HH24:00') as time,
                        COUNT(*) as count
                    FROM api_access_log 
                    WHERE timestamp > NOW() - INTERVAL '{interval_str}'
                    GROUP BY TO_CHAR(timestamp, 'HH24:00')
                    ORDER BY time
                """))
            else:  # day
                result = conn.execute(text("""
                    SELECT 
                        TO_CHAR(timestamp, 'Mon DD') as time,
                        COUNT(*) as count
                    FROM api_access_log 
                    WHERE timestamp > NOW() - INTERVAL '30 days'
                    GROUP BY TO_CHAR(timestamp, 'Mon DD')
                    ORDER BY time
                """))
            
            usage = []
            for row in result:
                usage.append({
                    "time": row[0],
                    "count": row[1]
                })
            
            return {"api_usage": usage}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API usage: {str(e)}")


@analytics_dashboard_router.get("/user-activity")
async def get_user_activity(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user activity statistics"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Get user registrations over time
            registrations = conn.execute(text("""
                SELECT 
                    TO_CHAR(created_at, 'Mon DD') as date,
                    COUNT(*) as count
                FROM users 
                WHERE created_at > NOW() - INTERVAL '30 days'
                GROUP BY TO_CHAR(created_at, 'Mon DD')
                ORDER BY MIN(created_at)
            """))
            
            registration_data = [{"date": row[0], "count": row[1]} for row in registrations]
            
            # Get login activity
            logins = conn.execute(text("""
                SELECT 
                    TO_CHAR(timestamp, 'Mon DD') as date,
                    COUNT(*) as count
                FROM auth_events 
                WHERE success = true 
                AND timestamp > NOW() - INTERVAL '30 days'
                GROUP BY TO_CHAR(timestamp, 'Mon DD')
                ORDER BY MIN(timestamp)
            """))
            
            login_data = [{"date": row[0], "count": row[1]} for row in logins]
            
            # Get users by tier
            tier_result = conn.execute(text("""
                SELECT tier, COUNT(*) as count 
                FROM users 
                GROUP BY tier
            """))
            
            users_by_tier = {row[0]: row[1] for row in tier_result}
            
            return {
                "user_activity": {
                    "registrations": registration_data,
                    "logins": login_data,
                    "users_by_tier": users_by_tier
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user activity: {str(e)}")


@analytics_dashboard_router.get("/top-endpoints")
async def get_top_endpoints(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 10
):
    """Get most accessed API endpoints"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    endpoint,
                    COUNT(*) as total_calls,
                    AVG(response_time) as avg_response_time
                FROM api_access_log 
                WHERE timestamp > NOW() - INTERVAL '7 days'
                GROUP BY endpoint
                ORDER BY total_calls DESC
                LIMIT :limit
            """), {"limit": limit})
            
            endpoints = []
            for row in result:
                endpoints.append({
                    "endpoint": row[0],
                    "total_calls": row[1],
                    "avg_response_time": round(float(row[2]), 2) if row[2] else 0
                })
            
            return {"top_endpoints": endpoints}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top endpoints: {str(e)}")


@analytics_dashboard_router.get("/error-rates")
async def get_error_rates(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get API error rates"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Get error rate over time
            result = conn.execute(text("""
                SELECT 
                    TO_CHAR(timestamp, 'HH24:00') as hour,
                    COUNT(*) FILTER (WHERE response_code >= 400) as errors,
                    COUNT(*) as total
                FROM api_access_log 
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                GROUP BY TO_CHAR(timestamp, 'HH24:00')
                ORDER BY hour
            """))
            
            error_rates = []
            for row in result:
                error_rate = (row[1] / row[2] * 100) if row[2] > 0 else 0
                error_rates.append({
                    "hour": row[0],
                    "error_count": row[1],
                    "total_requests": row[2],
                    "error_rate": round(error_rate, 2)
                })
            
            return {"error_rates": error_rates}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch error rates: {str(e)}")
