"""
Security Framework and Monitoring Dashboard
Comprehensive security infrastructure for weather operations platform
"""

import os
import json
import logging
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import threading
import schedule
from sqlalchemy import create_engine, text
from langchain.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import psutil
import socket
import ssl

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Security threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MonitoringCategory(Enum):
    """Categories of security monitoring"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    DATA_ACCESS = "data_access"
    SYSTEM_RESOURCES = "system_resources"
    API_USAGE = "api_usage"
    MODEL_SECURITY = "model_security"

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    id: str
    timestamp: datetime
    category: MonitoringCategory
    threat_level: ThreatLevel
    title: str
    description: str
    source_ip: Optional[str]
    user_id: Optional[str]
    affected_resources: List[str]
    indicators: Dict[str, Any]
    response_actions: List[str]
    status: str  # open, investigating, resolved, false_positive
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance and security metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_connections: int
    active_sessions: int
    failed_logins: int
    api_requests_per_minute: int
    threat_detections: int

class SecurityFramework:
    """Comprehensive security framework for weather operations"""
    
    def __init__(self, db_uri: str = None):
        """Initialize security framework"""
        self.db_uri = db_uri or os.getenv("DATABASE_URL")
        self.incidents = deque(maxlen=10000)  # Keep last 10k incidents in memory
        self.metrics_history = deque(maxlen=1440)  # 24 hours of minute-level metrics
        self.active_threats = {}
        self.monitoring_enabled = True
        self.alert_thresholds = self.setup_alert_thresholds()
        self.setup_security_infrastructure()
        self.start_monitoring()
    
    def setup_alert_thresholds(self) -> Dict:
        """Setup security alert thresholds"""
        return {
            "cpu_usage": 85.0,
            "memory_usage": 90.0,
            "disk_usage": 95.0,
            "failed_logins_per_hour": 10,
            "api_requests_per_minute": 1000,
            "network_connections": 500,
            "threat_score_threshold": 0.7
        }
    
    def setup_security_infrastructure(self):
        """Initialize security monitoring infrastructure"""
        try:
            if self.db_uri:
                self.engine = create_engine(self.db_uri)
                self.create_security_monitoring_tables()
            
            # Initialize threat detection models
            self.threat_detector = ThreatDetectionEngine()
            
            # Setup notification system using central NotificationManager
            try:
                from services.utils.notification_manager import get_notification_manager
                self.notification_system = get_notification_manager(engine=getattr(self, 'engine', None))
            except Exception:
                # Fallback to local SecurityNotificationSystem if import fails
                self.notification_system = SecurityNotificationSystem()
            
            logger.info("🔒 Security framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to setup security infrastructure: {e}")
    
    def create_security_monitoring_tables(self):
        """Create comprehensive security monitoring tables"""
        try:
            with self.engine.connect() as conn:
                # Security incidents table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS security_incidents (
                        id VARCHAR(50) PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        category VARCHAR(50),
                        threat_level VARCHAR(20),
                        title VARCHAR(200),
                        description TEXT,
                        source_ip VARCHAR(45),
                        user_id VARCHAR(50),
                        affected_resources JSONB,
                        indicators JSONB,
                        response_actions JSONB,
                        status VARCHAR(20) DEFAULT 'open',
                        assigned_to VARCHAR(50),
                        resolution_notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # System metrics monitoring
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cpu_usage FLOAT,
                        memory_usage FLOAT,
                        disk_usage FLOAT,
                        network_connections INTEGER,
                        active_sessions INTEGER,
                        failed_logins INTEGER,
                        api_requests_per_minute INTEGER,
                        threat_detections INTEGER
                    )
                """))
                
                # API access log
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS api_access_log (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        endpoint VARCHAR(200),
                        method VARCHAR(10),
                        user_id VARCHAR(50),
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        response_code INTEGER,
                        response_time FLOAT,
                        request_size INTEGER,
                        response_size INTEGER,
                        threat_score FLOAT DEFAULT 0.0
                    )
                """))
                
                # Network traffic analysis
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS network_traffic (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source_ip VARCHAR(45),
                        destination_ip VARCHAR(45),
                        port INTEGER,
                        protocol VARCHAR(10),
                        bytes_transferred BIGINT,
                        connection_duration FLOAT,
                        threat_indicators JSONB
                    )
                """))
                
                # Authentication events
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS auth_events (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        event_type VARCHAR(50),
                        user_id VARCHAR(50),
                        ip_address VARCHAR(45),
                        success BOOLEAN,
                        failure_reason VARCHAR(200),
                        session_id VARCHAR(100),
                        user_agent TEXT,
                        geolocation JSONB
                    )
                """))
                
                conn.commit()
                logger.info("Security monitoring tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create security monitoring tables: {e}")
    
    def start_monitoring(self):
        """Start continuous security monitoring"""
        if not self.monitoring_enabled:
            return
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        # Schedule periodic tasks
        schedule.every(1).minute.do(self.collect_system_metrics)
        schedule.every(5).minutes.do(self.analyze_threat_patterns)
        schedule.every(15).minutes.do(self.generate_security_alerts)
        schedule.every(1).hour.do(self.cleanup_old_data)
        
        logger.info("🔍 Security monitoring started")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_enabled:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def collect_system_metrics(self):
        """Collect current system performance and security metrics"""
        try:
            # System resource metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network_connections = len(psutil.net_connections())
            
            # Security-specific metrics
            failed_logins = self.count_failed_logins_last_hour()
            api_requests = self.count_api_requests_last_minute()
            threat_detections = self.count_threat_detections_last_minute()
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                network_connections=network_connections,
                active_sessions=self.count_active_sessions(),
                failed_logins=failed_logins,
                api_requests_per_minute=api_requests,
                threat_detections=threat_detections
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            self.store_system_metrics(metrics)
            
            # Check for threshold violations
            self.check_metric_thresholds(metrics)
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
    
    def check_metric_thresholds(self, metrics: SystemMetrics):
        """Check if metrics exceed security thresholds"""
        alerts = []
        
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append(f"High memory usage: {metrics.memory_usage:.1f}%")
        
        if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
            alerts.append(f"High disk usage: {metrics.disk_usage:.1f}%")
        
        if metrics.failed_logins > self.alert_thresholds["failed_logins_per_hour"]:
            alerts.append(f"High failed login rate: {metrics.failed_logins} attempts/hour")
        
        if metrics.api_requests_per_minute > self.alert_thresholds["api_requests_per_minute"]:
            alerts.append(f"High API request rate: {metrics.api_requests_per_minute} requests/minute")
        
        # Generate incidents for threshold violations
        for alert in alerts:
            self.create_security_incident(
                category=MonitoringCategory.SYSTEM_RESOURCES,
                threat_level=ThreatLevel.MEDIUM,
                title="System Resource Threshold Exceeded",
                description=alert,
                indicators=asdict(metrics)
            )
    
    def analyze_threat_patterns(self):
        """Analyze patterns for advanced threat detection"""
        try:
            # Analyze recent incidents for patterns
            recent_incidents = [i for i in self.incidents if i.timestamp > datetime.now() - timedelta(hours=1)]
            
            # Pattern detection algorithms
            self.detect_brute_force_attacks(recent_incidents)
            self.detect_anomalous_access_patterns()
            self.detect_data_exfiltration_attempts()
            
        except Exception as e:
            logger.error(f"Threat pattern analysis failed: {e}")
    
    def detect_brute_force_attacks(self, incidents: List[SecurityIncident]):
        """Detect brute force attack patterns"""
        ip_failures = defaultdict(int)
        user_failures = defaultdict(int)
        
        for incident in incidents:
            if incident.category == MonitoringCategory.AUTHENTICATION:
                if incident.source_ip:
                    ip_failures[incident.source_ip] += 1
                if incident.user_id:
                    user_failures[incident.user_id] += 1
        
        # Check for brute force thresholds
        for ip, count in ip_failures.items():
            if count > 20:  # 20 failures in 1 hour
                self.create_security_incident(
                    category=MonitoringCategory.AUTHENTICATION,
                    threat_level=ThreatLevel.HIGH,
                    title="Potential Brute Force Attack",
                    description=f"IP {ip} has {count} failed authentication attempts in the last hour",
                    source_ip=ip,
                    indicators={"failure_count": count, "time_window": "1_hour"}
                )
    
    def detect_anomalous_access_patterns(self):
        """Detect anomalous API access patterns"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    # Get recent API access patterns
                    result = conn.execute(text("""
                        SELECT ip_address, COUNT(*) as request_count,
                               AVG(response_time) as avg_response_time,
                               COUNT(DISTINCT endpoint) as unique_endpoints
                        FROM api_access_log 
                        WHERE timestamp > NOW() - INTERVAL '1 hour'
                        GROUP BY ip_address
                        HAVING COUNT(*) > 100
                    """))
                    
                    for row in result.fetchall():
                        ip, count, avg_time, endpoints = row
                        
                        # Check for suspicious patterns
                        if count > 500:  # High volume
                            self.create_security_incident(
                                category=MonitoringCategory.API_USAGE,
                                threat_level=ThreatLevel.MEDIUM,
                                title="High Volume API Access",
                                description=f"IP {ip} made {count} API requests in 1 hour",
                                source_ip=ip,
                                indicators={"request_count": count, "avg_response_time": avg_time}
                            )
                        
                        if endpoints > 50:  # Scanning behavior
                            self.create_security_incident(
                                category=MonitoringCategory.API_USAGE,
                                threat_level=ThreatLevel.HIGH,
                                title="Potential API Scanning",
                                description=f"IP {ip} accessed {endpoints} different endpoints",
                                source_ip=ip,
                                indicators={"unique_endpoints": endpoints, "scanning_behavior": True}
                            )
        except Exception as e:
            logger.error(f"Anomalous access pattern detection failed: {e}")
    
    def detect_data_exfiltration_attempts(self):
        """Detect potential data exfiltration"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    # Check for large data transfers
                    result = conn.execute(text("""
                        SELECT user_id, ip_address, SUM(response_size) as total_data
                        FROM api_access_log 
                        WHERE timestamp > NOW() - INTERVAL '1 hour'
                          AND response_size > 1048576  -- 1MB responses
                        GROUP BY user_id, ip_address
                        HAVING SUM(response_size) > 104857600  -- 100MB total
                    """))
                    
                    for row in result.fetchall():
                        user_id, ip, total_data = row
                        
                        self.create_security_incident(
                            category=MonitoringCategory.DATA_ACCESS,
                            threat_level=ThreatLevel.HIGH,
                            title="Potential Data Exfiltration",
                            description=f"User {user_id} from {ip} transferred {total_data/1048576:.1f}MB in 1 hour",
                            source_ip=ip,
                            user_id=user_id,
                            indicators={"data_transferred_mb": total_data/1048576}
                        )
        except Exception as e:
            logger.error(f"Data exfiltration detection failed: {e}")
    
    def create_security_incident(self, category: MonitoringCategory, threat_level: ThreatLevel,
                               title: str, description: str, **kwargs) -> SecurityIncident:
        """Create and store a security incident"""
        incident_id = hashlib.md5(
            f"{title}{datetime.now().isoformat()}{kwargs.get('source_ip', '')}".encode()
        ).hexdigest()[:16]
        
        incident = SecurityIncident(
            id=incident_id,
            timestamp=datetime.now(),
            category=category,
            threat_level=threat_level,
            title=title,
            description=description,
            source_ip=kwargs.get('source_ip'),
            user_id=kwargs.get('user_id'),
            affected_resources=kwargs.get('affected_resources', []),
            indicators=kwargs.get('indicators', {}),
            response_actions=self.generate_response_actions(threat_level, category),
            status="open"
        )
        
        # Store incident
        self.incidents.append(incident)
        self.store_security_incident(incident)
        
        # Send alerts for high/critical threats via central manager
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            try:
                # notification manager exposes notify(subject, message, level, metadata)
                self.notification_system.notify(
                    subject=f"Security Alert: {incident.title} ({incident.threat_level.value.upper()})",
                    message=f"{incident.description}\n\nIncident ID: {incident.id}\nCategory: {incident.category.value}",
                    level=incident.threat_level.value,
                    metadata={
                        'incident_id': incident.id,
                        'category': incident.category.value,
                        'source_ip': incident.source_ip,
                        'user_id': incident.user_id,
                        'response_actions': incident.response_actions
                    }
                )
            except Exception:
                # If central manager doesn't support notify, try legacy send
                try:
                    self.notification_system.send_security_alert(incident)
                except Exception as e:
                    logger.error(f"Failed to send security alert: {e}")
        
        logger.warning(f"🚨 Security incident created: {title} ({threat_level.value})")
        return incident
    
    def generate_response_actions(self, threat_level: ThreatLevel, category: MonitoringCategory) -> List[str]:
        """Generate appropriate response actions based on threat"""
        actions = []
        
        if threat_level == ThreatLevel.CRITICAL:
            actions.extend([
                "Immediately isolate affected systems",
                "Notify security team and management",
                "Begin incident response protocol",
                "Preserve forensic evidence"
            ])
        elif threat_level == ThreatLevel.HIGH:
            actions.extend([
                "Monitor closely for escalation",
                "Review and tighten access controls",
                "Notify security team",
                "Document incident details"
            ])
        elif threat_level == ThreatLevel.MEDIUM:
            actions.extend([
                "Increase monitoring frequency",
                "Review related logs",
                "Consider preventive measures"
            ])
        
        if category == MonitoringCategory.AUTHENTICATION:
            actions.append("Consider temporary account lockout")
        elif category == MonitoringCategory.NETWORK:
            actions.append("Analyze network traffic patterns")
        elif category == MonitoringCategory.DATA_ACCESS:
            actions.append("Review data access permissions")
        
        return actions
    
    def store_security_incident(self, incident: SecurityIncident):
        """Store security incident in database"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO security_incidents 
                        (id, timestamp, category, threat_level, title, description, 
                         source_ip, user_id, affected_resources, indicators, response_actions, status)
                        VALUES (:id, :timestamp, :category, :threat_level, :title, :description,
                                :source_ip, :user_id, :affected_resources, :indicators, :response_actions, :status)
                    """), {
                        "id": incident.id,
                        "timestamp": incident.timestamp,
                        "category": incident.category.value,
                        "threat_level": incident.threat_level.value,
                        "title": incident.title,
                        "description": incident.description,
                        "source_ip": incident.source_ip,
                        "user_id": incident.user_id,
                        "affected_resources": json.dumps(incident.affected_resources),
                        "indicators": json.dumps(incident.indicators),
                        "response_actions": json.dumps(incident.response_actions),
                        "status": incident.status
                    })
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to store security incident: {e}")
    
    def store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO system_metrics 
                        (timestamp, cpu_usage, memory_usage, disk_usage, network_connections,
                         active_sessions, failed_logins, api_requests_per_minute, threat_detections)
                        VALUES (:timestamp, :cpu_usage, :memory_usage, :disk_usage, :network_connections,
                                :active_sessions, :failed_logins, :api_requests_per_minute, :threat_detections)
                    """), asdict(metrics))
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to store system metrics: {e}")
    
    def count_failed_logins_last_hour(self) -> int:
        """Count failed login attempts in the last hour"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM auth_events 
                        WHERE timestamp > NOW() - INTERVAL '1 hour' 
                          AND success = FALSE
                    """))
                    return result.fetchone()[0]
        except:
            return 0
    
    def count_api_requests_last_minute(self) -> int:
        """Count API requests in the last minute"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM api_access_log 
                        WHERE timestamp > NOW() - INTERVAL '1 minute'
                    """))
                    return result.fetchone()[0]
        except:
            return 0
    
    def count_threat_detections_last_minute(self) -> int:
        """Count threat detections in the last minute"""
        count = 0
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        for incident in self.incidents:
            if incident.timestamp > one_minute_ago:
                count += 1
        return count
    
    def count_active_sessions(self) -> int:
        """Count currently active user sessions"""
        # This would typically integrate with your session management system
        return len(psutil.net_connections(kind='inet'))
    
    def get_security_dashboard_data(self) -> Dict:
        """Get comprehensive security dashboard data"""
        try:
            current_time = datetime.now()
            last_24h = current_time - timedelta(hours=24)
            
            dashboard_data = {
                "overview": {
                    "total_incidents_24h": len([i for i in self.incidents if i.timestamp > last_24h]),
                    "critical_incidents": len([i for i in self.incidents if i.threat_level == ThreatLevel.CRITICAL and i.timestamp > last_24h]),
                    "high_incidents": len([i for i in self.incidents if i.threat_level == ThreatLevel.HIGH and i.timestamp > last_24h]),
                    "open_incidents": len([i for i in self.incidents if i.status == "open"]),
                    "system_health": "healthy" if self.metrics_history and self.metrics_history[-1].cpu_usage < 80 else "warning"
                },
                "recent_incidents": [
                    {
                        "id": incident.id,
                        "timestamp": incident.timestamp.isoformat(),
                        "title": incident.title,
                        "threat_level": incident.threat_level.value,
                        "category": incident.category.value,
                        "status": incident.status
                    }
                    for incident in list(self.incidents)[-10:]  # Last 10 incidents
                ],
                "metrics": {
                    "current": asdict(self.metrics_history[-1]) if self.metrics_history else {},
                    "trend": self.calculate_metrics_trend()
                },
                "threat_categories": self.get_threat_category_breakdown(),
                "top_threat_sources": self.get_top_threat_sources(),
                "system_performance": self.get_system_performance_summary()
            }
            
            return dashboard_data
        except Exception as e:
            logger.error(f"Failed to get security dashboard data: {e}")
            return {"error": str(e)}
    
    def calculate_metrics_trend(self) -> Dict:
        """Calculate trend analysis for key metrics"""
        if len(self.metrics_history) < 2:
            return {}
        
        recent = list(self.metrics_history)[-60:]  # Last hour
        older = list(self.metrics_history)[-120:-60] if len(self.metrics_history) >= 120 else []
        
        if not older:
            return {}
        
        trends = {}
        for metric in ['cpu_usage', 'memory_usage', 'disk_usage', 'threat_detections']:
            recent_avg = np.mean([getattr(m, metric) for m in recent])
            older_avg = np.mean([getattr(m, metric) for m in older])
            
            if older_avg > 0:
                trend = ((recent_avg - older_avg) / older_avg) * 100
                trends[metric] = {
                    "current": recent_avg,
                    "previous": older_avg,
                    "change_percent": trend,
                    "direction": "up" if trend > 5 else "down" if trend < -5 else "stable"
                }
        
        return trends
    
    def get_threat_category_breakdown(self) -> Dict:
        """Get breakdown of threats by category"""
        last_24h = datetime.now() - timedelta(hours=24)
        recent_incidents = [i for i in self.incidents if i.timestamp > last_24h]
        
        categories = {}
        for incident in recent_incidents:
            category = incident.category.value
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return categories
    
    def get_top_threat_sources(self) -> List[Dict]:
        """Get top threat source IPs"""
        last_24h = datetime.now() - timedelta(hours=24)
        recent_incidents = [i for i in self.incidents if i.timestamp > last_24h and i.source_ip]
        
        ip_counts = defaultdict(int)
        for incident in recent_incidents:
            ip_counts[incident.source_ip] += 1
        
        return [
            {"ip": ip, "incident_count": count}
            for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def get_system_performance_summary(self) -> Dict:
        """Get system performance summary"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        return {
            "cpu_usage": latest.cpu_usage,
            "memory_usage": latest.memory_usage,
            "disk_usage": latest.disk_usage,
            "network_connections": latest.network_connections,
            "status": "healthy" if latest.cpu_usage < 80 and latest.memory_usage < 85 else "warning"
        }
    
    def generate_security_alerts(self):
        """Generate and send security alerts"""
        # This would be called periodically to check for alerting conditions
        pass
    
    def cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            # Remove incidents older than 30 days from database
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        DELETE FROM security_incidents 
                        WHERE timestamp < NOW() - INTERVAL '30 days'
                    """))
                    conn.execute(text("""
                        DELETE FROM system_metrics 
                        WHERE timestamp < NOW() - INTERVAL '7 days'
                    """))
                    conn.execute(text("""
                        DELETE FROM api_access_log 
                        WHERE timestamp < NOW() - INTERVAL '7 days'
                    """))
                    conn.commit()
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")

class ThreatDetectionEngine:
    """Advanced threat detection using machine learning"""
    
    def __init__(self):
        """Initialize threat detection engine"""
        self.models = {}
        self.initialize_detection_models()
    
    def initialize_detection_models(self):
        """Initialize threat detection models"""
        # Placeholder for ML models
        # In production, this would load trained models for:
        # - Anomaly detection
        # - Behavioral analysis
        # - Pattern recognition
        pass
    
    def calculate_threat_score(self, request_data: Dict) -> float:
        """Calculate threat score for a request"""
        score = 0.0
        
        # Basic heuristics (replace with ML models in production)
        if request_data.get('response_time', 0) > 5000:  # Very slow response
            score += 0.2
        
        if request_data.get('request_size', 0) > 10485760:  # Large request (10MB)
            score += 0.3
        
        user_agent = request_data.get('user_agent', '').lower()
        suspicious_agents = ['bot', 'crawler', 'scanner', 'curl', 'wget']
        if any(agent in user_agent for agent in suspicious_agents):
            score += 0.4
        
        return min(score, 1.0)

class SecurityNotificationSystem:
    """Security alert notification system"""
    
    def __init__(self):
        """Initialize notification system"""
        self.email_enabled = bool(os.getenv('SMTP_SERVER'))
        self.webhook_url = os.getenv('SECURITY_WEBHOOK_URL')
        self.setup_notification_channels()
    
    def setup_notification_channels(self):
        """Setup notification channels"""
        if self.email_enabled:
            self.smtp_server = os.getenv('SMTP_SERVER')
            self.smtp_port = int(os.getenv('SMTP_PORT', 587))
            self.smtp_username = os.getenv('SMTP_USERNAME')
            self.smtp_password = os.getenv('SMTP_PASSWORD')
    
    def send_security_alert(self, incident: SecurityIncident):
        """Send security alert through configured channels"""
        try:
            if incident.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                if self.email_enabled:
                    self.send_email_alert(incident)
                
                if self.webhook_url:
                    self.send_webhook_alert(incident)
        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")
    
    def send_email_alert(self, incident: SecurityIncident):
        """Send email security alert"""
        try:
            subject = f"🚨 Security Alert: {incident.title} ({incident.threat_level.value.upper()})"
            body = f"""
Security Incident Detected

Incident ID: {incident.id}
Timestamp: {incident.timestamp.isoformat()}
Threat Level: {incident.threat_level.value.upper()}
Category: {incident.category.value}

Description:
{incident.description}

Source IP: {incident.source_ip or 'Unknown'}
User ID: {incident.user_id or 'Unknown'}

Recommended Actions:
{chr(10).join(f"• {action}" for action in incident.response_actions)}

Please investigate immediately.
"""
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = os.getenv('SECURITY_ALERT_EMAIL', 'security@company.com')
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"📧 Security alert email sent for incident {incident.id}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def send_webhook_alert(self, incident: SecurityIncident):
        """Send webhook security alert"""
        try:
            payload = {
                "alert_type": "security_incident",
                "incident_id": incident.id,
                "timestamp": incident.timestamp.isoformat(),
                "threat_level": incident.threat_level.value,
                "title": incident.title,
                "description": incident.description,
                "category": incident.category.value,
                "source_ip": incident.source_ip,
                "user_id": incident.user_id
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"🔗 Security alert webhook sent for incident {incident.id}")
            else:
                logger.error(f"Webhook alert failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

# Global security framework instance
security_framework_instance = None

def get_security_framework():
    """Get or create global security framework instance"""
    global security_framework_instance
    if security_framework_instance is None:
        security_framework_instance = SecurityFramework()
    return security_framework_instance

# API functions for integration
def log_api_access(endpoint: str, method: str, user_id: str, ip_address: str, 
                   response_code: int, response_time: float, **kwargs):
    """Log API access for security monitoring"""
    try:
        framework = get_security_framework()
        threat_detector = ThreatDetectionEngine()
        
        request_data = {
            'endpoint': endpoint,
            'method': method,
            'user_id': user_id,
            'ip_address': ip_address,
            'response_code': response_code,
            'response_time': response_time,
            'user_agent': kwargs.get('user_agent', ''),
            'request_size': kwargs.get('request_size', 0),
            'response_size': kwargs.get('response_size', 0)
        }
        
        threat_score = threat_detector.calculate_threat_score(request_data)
        
        if hasattr(framework, 'engine'):
            with framework.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO api_access_log 
                    (timestamp, endpoint, method, user_id, ip_address, user_agent,
                     response_code, response_time, request_size, response_size, threat_score)
                    VALUES (NOW(), :endpoint, :method, :user_id, :ip_address, :user_agent,
                            :response_code, :response_time, :request_size, :response_size, :threat_score)
                """), {**request_data, 'threat_score': threat_score})
                conn.commit()
        
        # Generate incident for high threat scores
        if threat_score > 0.7:
            framework.create_security_incident(
                category=MonitoringCategory.API_USAGE,
                threat_level=ThreatLevel.HIGH if threat_score > 0.8 else ThreatLevel.MEDIUM,
                title="Suspicious API Access Detected",
                description=f"High threat score ({threat_score:.2f}) for {method} {endpoint}",
                source_ip=ip_address,
                user_id=user_id,
                indicators={'threat_score': threat_score, **request_data}
            )
    except Exception as e:
        logger.error(f"Failed to log API access: {e}")

def log_authentication_event(event_type: str, user_id: str, ip_address: str, 
                            success: bool, **kwargs):
    """Log authentication event for security monitoring"""
    try:
        framework = get_security_framework()
        
        if hasattr(framework, 'engine'):
            with framework.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO auth_events 
                    (timestamp, event_type, user_id, ip_address, success, failure_reason,
                     session_id, user_agent, geolocation)
                    VALUES (NOW(), :event_type, :user_id, :ip_address, :success, :failure_reason,
                            :session_id, :user_agent, :geolocation)
                """), {
                    'event_type': event_type,
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'success': success,
                    'failure_reason': kwargs.get('failure_reason'),
                    'session_id': kwargs.get('session_id'),
                    'user_agent': kwargs.get('user_agent'),
                    'geolocation': json.dumps(kwargs.get('geolocation', {}))
                })
                conn.commit()
        
        # Generate incident for failed logins
        if not success:
            framework.create_security_incident(
                category=MonitoringCategory.AUTHENTICATION,
                threat_level=ThreatLevel.LOW,
                title="Authentication Failure",
                description=f"Failed {event_type} for user {user_id} from {ip_address}",
                source_ip=ip_address,
                user_id=user_id,
                indicators={'event_type': event_type, 'failure_reason': kwargs.get('failure_reason')}
            )
    except Exception as e:
        logger.error(f"Failed to log authentication event: {e}")

# Test function
if __name__ == "__main__":
    print("🔒 Testing Security Framework...")
    
    framework = get_security_framework()
    
    # Test incident creation
    test_incident = framework.create_security_incident(
        category=MonitoringCategory.AUTHENTICATION,
        threat_level=ThreatLevel.MEDIUM,
        title="Test Security Incident",
        description="This is a test incident for framework validation",
        source_ip="192.168.1.100",
        user_id="test_user"
    )
    
    print(f"✅ Test incident created: {test_incident.id}")
    
    # Test dashboard data
    dashboard_data = framework.get_security_dashboard_data()
    print(f"📊 Dashboard data: {len(dashboard_data)} sections")
    
    # Test API logging
    log_api_access(
        endpoint="/api/weather/data",
        method="GET",
        user_id="test_user",
        ip_address="192.168.1.100",
        response_code=200,
        response_time=150.5
    )
    
    print("🔍 Security framework testing complete!")