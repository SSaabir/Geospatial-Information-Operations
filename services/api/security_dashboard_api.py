"""Security Dashboard API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from sqlalchemy import text
from datetime import datetime, timedelta

from security.auth_middleware import get_current_user
from db_config import DatabaseConfig
from models.user import UserDB

security_dashboard_router = APIRouter(prefix="/security-dashboard", tags=["security-dashboard"])

def get_db():
    """Dependency to get database connection"""
    db_config = DatabaseConfig()
    engine = db_config.get_engine()
    return engine


@security_dashboard_router.get("/overview")
async def get_security_overview(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    time_range: str = "24h"
):
    """Get security dashboard overview statistics"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        # Parse time range
        hours = 24
        if time_range == "1h":
            hours = 1
        elif time_range == "7d":
            hours = 168
        elif time_range == "30d":
            hours = 720
        
        with db.connect() as conn:
            # Get total incidents in time range
            total_incidents = conn.execute(text("""
                SELECT COUNT(*) FROM security_alerts 
                WHERE timestamp > NOW() - INTERVAL ':hours hours'
            """).bindparams(hours=hours)).scalar() or 0
            
            # Get critical incidents
            critical_incidents = conn.execute(text("""
                SELECT COUNT(*) FROM security_alerts 
                WHERE severity = 'critical' 
                AND timestamp > NOW() - INTERVAL ':hours hours'
            """).bindparams(hours=hours)).scalar() or 0
            
            # Get high priority incidents
            high_incidents = conn.execute(text("""
                SELECT COUNT(*) FROM security_alerts 
                WHERE severity = 'high' 
                AND timestamp > NOW() - INTERVAL ':hours hours'
            """).bindparams(hours=hours)).scalar() or 0
            
            # Get open incidents (assuming recent ones are open)
            open_incidents = conn.execute(text("""
                SELECT COUNT(*) FROM security_alerts 
                WHERE timestamp > NOW() - INTERVAL '7 days'
            """)).scalar() or 0
            
            # Calculate security score (based on incident severity)
            total_alerts = conn.execute(text("SELECT COUNT(*) FROM security_alerts")).scalar() or 1
            security_score = max(0, 100 - (critical_incidents * 10 + high_incidents * 5))
            
            # Get blocked attempts from auth_events
            blocked_attempts = conn.execute(text("""
                SELECT COUNT(*) FROM auth_events 
                WHERE success = false 
                AND timestamp > NOW() - INTERVAL ':hours hours'
            """).bindparams(hours=hours)).scalar() or 0
            
            # Get requests per hour from api_access_log
            requests_per_hour = conn.execute(text("""
                SELECT COUNT(*) / :hours as avg_per_hour
                FROM api_access_log 
                WHERE timestamp > NOW() - INTERVAL ':hours hours'
            """).bindparams(hours=hours)).scalar() or 0
            
            return {
                "overview": {
                    "total_incidents_24h": total_incidents,
                    "critical_incidents": critical_incidents,
                    "high_incidents": high_incidents,
                    "open_incidents": open_incidents,
                    "system_health": "healthy" if critical_incidents == 0 else "warning",
                    "threat_score": min(100, critical_incidents * 10 + high_incidents * 5),
                    "security_score": int(security_score),
                    "active_threats": critical_incidents + high_incidents
                },
                "metrics": {
                    "requests_per_hour": int(requests_per_hour),
                    "blocked_attempts": blocked_attempts,
                    "data_processed_gb": 0,  # Placeholder
                    "uptime_percentage": 99.97  # Placeholder
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch security overview: {str(e)}")


@security_dashboard_router.get("/incidents")
async def get_security_incidents(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db),
    limit: int = 20
):
    """Get recent security incidents"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    id,
                    timestamp,
                    threat_type,
                    severity,
                    source,
                    description,
                    ip_address
                FROM security_alerts 
                ORDER BY timestamp DESC 
                LIMIT :limit
            """), {"limit": limit})
            
            incidents = []
            for row in result:
                incidents.append({
                    "id": row[0],
                    "timestamp": row[1].isoformat() if row[1] else None,
                    "title": row[2] or "Security Alert",
                    "threat_level": row[3] or "medium",
                    "category": row[2] or "unknown",
                    "status": "investigating",
                    "source": row[6] or row[4] or "Unknown",
                    "description": row[5] or f"{row[2]} detected"
                })
            
            return {"incidents": incidents}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch security incidents: {str(e)}")


@security_dashboard_router.get("/threat-sources")
async def get_threat_sources(
    current_user: UserDB = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get threat sources analysis"""
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        with db.connect() as conn:
            # Get threat sources grouped by IP or source
            result = conn.execute(text("""
                SELECT 
                    COALESCE(source, 'Unknown') as country,
                    COUNT(*) as count
                FROM security_alerts 
                WHERE timestamp > NOW() - INTERVAL '30 days'
                GROUP BY source
                ORDER BY count DESC
                LIMIT 10
            """))
            
            total = conn.execute(text("""
                SELECT COUNT(*) FROM security_alerts 
                WHERE timestamp > NOW() - INTERVAL '30 days'
            """)).scalar() or 1
            
            sources = []
            for row in result:
                count = row[1]
                sources.append({
                    "country": row[0],
                    "count": count,
                    "percentage": round((count / total) * 100, 1)
                })
            
            return {"threat_sources": sources}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch threat sources: {str(e)}")
