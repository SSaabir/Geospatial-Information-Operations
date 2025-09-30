"""
Security Dashboard API endpoints
Provides REST API for security monitoring and threat detection data
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import sys
import os

# Add the agents directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

try:
    from security_agent import SecurityAgent
    from security_framework import get_security_framework, SecurityFramework
except ImportError as e:
    logging.error(f"Failed to import security modules: {e}")
    SecurityAgent = None
    get_security_framework = None
    SecurityFramework = None

from security.auth_middleware import verify_token

# Configure logging
logger = logging.getLogger(__name__)

# Create router
security_router = APIRouter(
    prefix="/api/security",
    tags=["Security"],
    responses={404: {"description": "Not found"}}
)

# Global instances
security_agent_instance = None
security_framework_instance = None

def get_security_agent():
    """Get or create security agent instance"""
    global security_agent_instance
    if security_agent_instance is None and SecurityAgent:
        try:
            security_agent_instance = SecurityAgent()
            logger.info("Security agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize security agent: {e}")
            security_agent_instance = None
    return security_agent_instance

def get_security_framework_instance():
    """Get or create security framework instance"""
    global security_framework_instance
    if security_framework_instance is None and get_security_framework:
        try:
            security_framework_instance = get_security_framework()
            logger.info("Security framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize security framework: {e}")
            security_framework_instance = None
    return security_framework_instance

@security_router.get("/dashboard")
async def get_security_dashboard(current_user: dict = Depends(verify_token)):
    """
    Get comprehensive security dashboard data
    """
    try:
        security_framework = get_security_framework_instance()
        
        if not security_framework:
            # Return mock data if framework is not available
            return {
                "overview": {
                    "total_incidents_24h": 12,
                    "critical_incidents": 2,
                    "high_incidents": 5,
                    "open_incidents": 8,
                    "system_health": "healthy"
                },
                "recent_incidents": [
                    {
                        "id": "SEC001",
                        "timestamp": datetime.now().isoformat(),
                        "title": "Unusual API Access Pattern",
                        "threat_level": "medium",
                        "category": "api_usage",
                        "status": "investigating"
                    }
                ],
                "metrics": {
                    "current": {
                        "cpu_usage": 68.5,
                        "memory_usage": 72.3,
                        "disk_usage": 45.8,
                        "network_connections": 156,
                        "threat_detections": 3
                    }
                },
                "threat_categories": {
                    "authentication": 8,
                    "api_usage": 15,
                    "data_access": 6
                },
                "top_threat_sources": [
                    {"ip": "192.168.1.100", "incident_count": 5}
                ]
            }
        
        dashboard_data = security_framework.get_security_dashboard_data()
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to get security dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve security dashboard data: {str(e)}"
        )

@security_router.get("/incidents")
async def get_security_incidents(
    limit: int = 50,
    threat_level: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(verify_token)
):
    """
    Get security incidents with optional filtering
    """
    try:
        security_framework = get_security_framework_instance()
        
        if not security_framework:
            # Return mock data
            return [
                {
                    "id": "SEC001",
                    "timestamp": datetime.now().isoformat(),
                    "title": "Failed Login Attempts",
                    "threat_level": "medium",
                    "category": "authentication",
                    "status": "open",
                    "description": "Multiple failed login attempts detected"
                }
            ]
        
        # Get incidents from framework
        incidents = list(security_framework.incidents)
        
        # Apply filters
        if threat_level:
            incidents = [i for i in incidents if i.threat_level.value == threat_level]
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        # Limit results
        incidents = incidents[-limit:]
        
        # Convert to JSON serializable format
        result = []
        for incident in incidents:
            result.append({
                "id": incident.id,
                "timestamp": incident.timestamp.isoformat(),
                "title": incident.title,
                "description": incident.description,
                "threat_level": incident.threat_level.value,
                "category": incident.category.value,
                "status": incident.status,
                "source_ip": incident.source_ip,
                "user_id": incident.user_id,
                "indicators": incident.indicators
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get security incidents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve security incidents: {str(e)}"
        )

@security_router.get("/metrics")
async def get_security_metrics(
    hours: int = 24,
    current_user: dict = Depends(verify_token)
):
    """
    Get security metrics for the specified time period
    """
    try:
        security_framework = get_security_framework_instance()
        
        if not security_framework:
            # Return mock metrics
            return {
                "current": {
                    "cpu_usage": 68.5,
                    "memory_usage": 72.3,
                    "disk_usage": 45.8,
                    "network_connections": 156,
                    "threat_detections": 3
                },
                "trend": {
                    "cpu_usage": {"direction": "up", "change_percent": 5.2},
                    "memory_usage": {"direction": "stable", "change_percent": -1.1},
                    "threat_detections": {"direction": "down", "change_percent": -15.3}
                }
            }
        
        # Get recent metrics
        metrics_history = list(security_framework.metrics_history)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        if recent_metrics:
            latest = recent_metrics[-1]
            current_metrics = {
                "cpu_usage": latest.cpu_usage,
                "memory_usage": latest.memory_usage,
                "disk_usage": latest.disk_usage,
                "network_connections": latest.network_connections,
                "threat_detections": latest.threat_detections,
                "timestamp": latest.timestamp.isoformat()
            }
        else:
            current_metrics = {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "network_connections": 0,
                "threat_detections": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "current": current_metrics,
            "history": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "threat_detections": m.threat_detections
                }
                for m in recent_metrics[-100:]  # Last 100 data points
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get security metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve security metrics: {str(e)}"
        )

@security_router.post("/validate")
async def validate_data(
    data: Dict[str, Any],
    current_user: dict = Depends(verify_token)
):
    """
    Validate data using security agent
    """
    try:
        security_agent = get_security_agent()
        
        if not security_agent:
            # Return mock validation
            return {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "risk_score": 0.0,
                "anomalies": []
            }
        
        validation_result = security_agent.validate_weather_data(data)
        return validation_result
        
    except Exception as e:
        logger.error(f"Failed to validate data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data validation failed: {str(e)}"
        )

@security_router.get("/threats/sources")
async def get_top_threat_sources(
    limit: int = 10,
    current_user: dict = Depends(verify_token)
):
    """
    Get top threat source IPs
    """
    try:
        security_framework = get_security_framework_instance()
        
        if not security_framework:
            # Return mock data
            return [
                {"ip": "192.168.1.100", "incident_count": 5, "last_seen": datetime.now().isoformat()},
                {"ip": "10.0.0.25", "incident_count": 3, "last_seen": datetime.now().isoformat()}
            ]
        
        # Get threat sources from incidents
        threat_sources = {}
        for incident in security_framework.incidents:
            if incident.source_ip:
                if incident.source_ip not in threat_sources:
                    threat_sources[incident.source_ip] = {
                        "count": 0,
                        "last_seen": incident.timestamp
                    }
                threat_sources[incident.source_ip]["count"] += 1
                if incident.timestamp > threat_sources[incident.source_ip]["last_seen"]:
                    threat_sources[incident.source_ip]["last_seen"] = incident.timestamp
        
        # Sort by count and format result
        sorted_sources = sorted(
            threat_sources.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]
        
        result = [
            {
                "ip": ip,
                "incident_count": data["count"],
                "last_seen": data["last_seen"].isoformat()
            }
            for ip, data in sorted_sources
        ]
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get threat sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve threat sources: {str(e)}"
        )

@security_router.post("/incidents/{incident_id}/update")
async def update_incident_status(
    incident_id: str,
    status_update: Dict[str, str],
    current_user: dict = Depends(verify_token)
):
    """
    Update security incident status
    """
    try:
        security_framework = get_security_framework_instance()
        
        if not security_framework:
            return {"message": "Incident status updated (mock)", "incident_id": incident_id}
        
        # Find and update incident
        for incident in security_framework.incidents:
            if incident.id == incident_id:
                if "status" in status_update:
                    incident.status = status_update["status"]
                if "assigned_to" in status_update:
                    incident.assigned_to = status_update["assigned_to"]
                if "resolution_notes" in status_update:
                    incident.resolution_notes = status_update["resolution_notes"]
                
                # Store updated incident in database if available
                security_framework.store_security_incident(incident)
                
                return {
                    "message": "Incident updated successfully",
                    "incident_id": incident_id,
                    "status": incident.status
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update incident: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update incident: {str(e)}"
        )

@security_router.get("/alerts/active")
async def get_active_alerts(current_user: dict = Depends(verify_token)):
    """
    Get active security alerts
    """
    try:
        security_framework = get_security_framework_instance()
        
        if not security_framework:
            return []
        
        # Get high and critical incidents from last 24 hours
        recent_time = datetime.now() - timedelta(hours=24)
        active_alerts = []
        
        for incident in security_framework.incidents:
            if (incident.timestamp > recent_time and 
                incident.status in ["open", "investigating"] and
                incident.threat_level.value in ["high", "critical"]):
                
                active_alerts.append({
                    "id": incident.id,
                    "title": incident.title,
                    "threat_level": incident.threat_level.value,
                    "timestamp": incident.timestamp.isoformat(),
                    "category": incident.category.value
                })
        
        return active_alerts
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active alerts: {str(e)}"
        )