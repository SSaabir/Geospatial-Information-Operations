"""Admin dashboard API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from sqlalchemy import text
from datetime import datetime, timedelta

from security.auth_middleware import verify_token
from db_config import DatabaseConfig
from models.user import UserDB
from security.auth_middleware import get_current_user

admin_router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    """Dependency to get database connection"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    return engine


@admin_router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get admin dashboard statistics (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Get total users count
            total_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            
            # Get active users (logged in within last 24 hours)
            active_users = conn.execute(text("""
                SELECT COUNT(*) FROM users 
                WHERE last_login > NOW() - INTERVAL '24 hours'
            """)).scalar()
            
            # Get users by tier
            users_by_tier = {}
            tier_result = conn.execute(text("""
                SELECT tier, COUNT(*) as count 
                FROM users 
                GROUP BY tier
            """))
            for row in tier_result:
                users_by_tier[row[0]] = row[1]
            
            # Get total notifications
            total_notifications = conn.execute(text("SELECT COUNT(*) FROM notifications")).scalar()
            
            # Get security alerts count (last 7 days)
            security_alerts = conn.execute(text("""
                SELECT COUNT(*) FROM security_alerts 
                WHERE timestamp > NOW() - INTERVAL '7 days'
            """)).scalar() or 0
            
            # Get security incidents count
            security_incidents = conn.execute(text("""
                SELECT COUNT(*) FROM security_incidents 
                WHERE timestamp > NOW() - INTERVAL '7 days'
            """)).scalar() or 0
            
            # Get system metrics if available
            system_metrics = {}
            try:
                metrics_result = conn.execute(text("""
                    SELECT metric_name, metric_value 
                    FROM system_metrics 
                    WHERE timestamp > NOW() - INTERVAL '1 hour'
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """))
                for row in metrics_result:
                    system_metrics[row[0]] = float(row[1]) if row[1] else 0
            except:
                # Table might not have data
                pass
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "users_by_tier": users_by_tier,
                "total_notifications": total_notifications,
                "security_alerts": security_alerts,
                "security_incidents": security_incidents,
                "system_metrics": system_metrics
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@admin_router.get("/dashboard/users/recent")
async def get_recent_users(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 10
):
    """Get recently active users (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    id, 
                    username, 
                    email, 
                    tier, 
                    is_admin,
                    last_login,
                    created_at
                FROM users 
                ORDER BY last_login DESC NULLS LAST
                LIMIT :limit
            """), {"limit": limit})
            
            users = []
            for row in result:
                # Handle timezone-aware datetime
                last_login_time = row[5]
                if last_login_time:
                    # Make datetime timezone-naive if it's timezone-aware
                    if last_login_time.tzinfo is not None:
                        last_login_time = last_login_time.replace(tzinfo=None)
                    is_online = (datetime.now() - last_login_time).seconds < 3600
                else:
                    is_online = False
                
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "tier": row[3],
                    "is_admin": row[4],
                    "last_login": row[5].isoformat() if row[5] else None,
                    "created_at": row[6].isoformat() if row[6] else None,
                    "status": "online" if is_online else "offline"
                })
            
            return {"users": users}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent users: {str(e)}")


@admin_router.get("/dashboard/activity")
async def get_user_activity(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user activity over time (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Get auth events for last 24 hours grouped by hour
            result = conn.execute(text("""
                SELECT 
                    TO_CHAR(timestamp, 'HH24:00') as hour,
                    COUNT(*) as count
                FROM auth_events 
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND success = true
                GROUP BY TO_CHAR(timestamp, 'HH24:00')
                ORDER BY hour
            """))
            
            total_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            
            activity = []
            for row in result:
                activity.append({
                    "time": row[0] if row[0] else "N/A",
                    "active": row[1],
                    "total": total_users
                })
            
            return {"activity": activity}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user activity: {str(e)}")


@admin_router.get("/dashboard/alerts")
async def get_system_alerts(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 10
):
    """Get recent system alerts (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        alerts = []
        
        with db.connect() as conn:
            # Get security alerts
            security_result = conn.execute(text("""
                SELECT 
                    id,
                    threat_type,
                    description,
                    severity,
                    timestamp
                FROM security_alerts 
                WHERE timestamp > NOW() - INTERVAL '7 days'
                ORDER BY timestamp DESC 
                LIMIT :limit
            """), {"limit": limit})
            
            for row in security_result:
                alerts.append({
                    "id": row[0],
                    "type": row[3] if row[3] else "warning",  # severity
                    "message": row[2] if row[2] else f"{row[1]} detected",  # description or threat_type
                    "time": row[4].strftime('%H:%M') if row[4] else "N/A",
                    "source": "security"
                })
            
            return {"alerts": alerts}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system alerts: {str(e)}")


@admin_router.get("/dashboard/notifications")
async def get_admin_notifications(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 50,
    level: str = None,
    unread_only: bool = False
):
    """Get all notifications for admin dashboard (admin only)
    
    This endpoint returns:
    - System-wide notifications (user_id IS NULL) - visible to all admins
    - All user-specific notifications - for admin overview
    """
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Build query with filters
            query = """
                SELECT 
                    n.id, 
                    n.timestamp, 
                    n.level, 
                    n.subject, 
                    n.message, 
                    n.metadata,
                    n.read,
                    n.user_id,
                    u.username
                FROM notifications n
                LEFT JOIN users u ON n.user_id = u.id
                WHERE 1=1
            """
            params = {"limit": limit}
            
            if level:
                query += " AND n.level = :level"
                params["level"] = level
            
            if unread_only:
                query += " AND n.read = false"
            
            query += " ORDER BY n.timestamp DESC LIMIT :limit"
            
            result = conn.execute(text(query), params)
            notifications = []
            
            import json
            for row in result:
                # Parse metadata from JSONB
                metadata = row[5] if row[5] else {}
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                notifications.append({
                    "id": row[0],
                    "timestamp": row[1].isoformat() if row[1] else None,
                    "level": row[2],
                    "subject": row[3],
                    "message": row[4],
                    "metadata": metadata,
                    "read": row[6] if row[6] is not None else False,
                    "user_id": row[7],
                    "username": row[8] if row[8] else "System",
                    "is_system_wide": row[7] is None
                })
            
            # Get unread count
            unread_count_query = "SELECT COUNT(*) FROM notifications WHERE read = false"
            if level:
                unread_count_query += " AND level = :level"
            
            unread_count = conn.execute(text(unread_count_query), params if level else {}).scalar()
            
            return {
                "notifications": notifications,
                "total": len(notifications),
                "unread_count": unread_count or 0
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin notifications: {str(e)}")
