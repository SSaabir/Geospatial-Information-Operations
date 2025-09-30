"""
Security Agent for Geospatial Weather Operations
Provides comprehensive security monitoring, threat detection, and data validation
"""

import os
import json
import hashlib
import time
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import psycopg2
from langchain.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from dotenv import load_dotenv
import ipaddress
import hashlib
import jwt
from cryptography.fernet import Fernet
import bcrypt

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM for security analysis
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1  # Low temperature for consistent security decisions
)

class SecurityLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    DATA_INJECTION = "data_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ANOMALOUS_PATTERN = "anomalous_pattern"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MALFORMED_REQUEST = "malformed_request"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    DATA_CORRUPTION = "data_corruption"

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    id: str
    timestamp: datetime
    threat_type: ThreatType
    severity: SecurityLevel
    source: str
    description: str
    affected_data: Optional[str]
    remediation: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Optional[Dict] = None

class SecurityState(TypedDict):
    """State for security agent workflow"""
    input_data: Any
    validation_results: Optional[Dict]
    threat_analysis: Optional[Dict]
    security_alerts: Optional[List[SecurityAlert]]
    risk_score: Optional[float]
    recommendations: Optional[List[str]]
    output: str
    error: Optional[str]

class SecurityAgent:
    """Advanced security monitoring and validation agent"""
    
    def __init__(self, db_uri: str = None):
        """Initialize security agent"""
        self.db_uri = db_uri or os.getenv("DATABASE_URL")
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher_suite = Fernet(self.encryption_key)
        self.session_store = {}
        self.rate_limit_store = {}
        self.suspicious_patterns = []
        self.setup_security_monitoring()
    
    def setup_security_monitoring(self):
        """Initialize security monitoring components"""
        try:
            # Connect to database for security logging
            if self.db_uri:
                self.engine = create_engine(self.db_uri)
                self.create_security_tables()
        except Exception as e:
            logger.error(f"Failed to setup security monitoring: {e}")
    
    def create_security_tables(self):
        """Create security monitoring tables"""
        try:
            with self.engine.connect() as conn:
                # Security alerts table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS security_alerts (
                        id VARCHAR(50) PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        threat_type VARCHAR(50),
                        severity VARCHAR(20),
                        source VARCHAR(100),
                        description TEXT,
                        affected_data VARCHAR(200),
                        remediation TEXT,
                        user_id VARCHAR(50),
                        ip_address VARCHAR(45),
                        metadata JSONB
                    )
                """))
                
                # Security audit log
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS security_audit_log (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        action VARCHAR(100),
                        user_id VARCHAR(50),
                        ip_address VARCHAR(45),
                        resource VARCHAR(200),
                        success BOOLEAN,
                        details JSONB
                    )
                """))
                
                # Data validation log
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS data_validation_log (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_source VARCHAR(100),
                        validation_type VARCHAR(50),
                        status VARCHAR(20),
                        errors_found INTEGER DEFAULT 0,
                        details JSONB
                    )
                """))
                
                conn.commit()
                logger.info("Security tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create security tables: {e}")
    
    def validate_weather_data(self, data: Any, source: str = "unknown") -> Dict:
        """Validate weather data for anomalies and injection attacks"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "risk_score": 0.0,
            "anomalies": []
        }
        
        try:
            # Convert data to DataFrame if needed
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                validation_results["errors"].append("Invalid data format")
                validation_results["is_valid"] = False
                return validation_results
            
            # Check for SQL injection patterns
            sql_injection_patterns = [
                r"union\s+select", r"drop\s+table", r"delete\s+from",
                r"insert\s+into", r"update\s+set", r"or\s+1\s*=\s*1",
                r";\s*--", r"'\s*or\s*'", r"exec\s*\(", r"script\s*>",
                r"<\s*script", r"javascript:", r"vbscript:", r"onload\s*="
            ]
            
            for column in df.columns:
                if df[column].dtype == 'object':
                    for value in df[column].astype(str):
                        for pattern in sql_injection_patterns:
                            if re.search(pattern, value.lower()):
                                validation_results["errors"].append(
                                    f"Potential SQL injection in {column}: {value}"
                                )
                                validation_results["risk_score"] += 0.3
                                validation_results["is_valid"] = False
            
            # Validate weather parameter ranges
            weather_ranges = {
                "temperature": (-50, 60),  # Celsius
                "tempmax": (-50, 60),
                "tempmin": (-50, 60),
                "humidity": (0, 100),
                "pressure": (870, 1085),  # hPa
                "windspeed": (0, 200),  # km/h
                "cloudcover": (0, 100),
                "visibility": (0, 50),  # km
                "uvindex": (0, 15)
            }
            
            for param, (min_val, max_val) in weather_ranges.items():
                if param in df.columns:
                    outliers = df[(df[param] < min_val) | (df[param] > max_val)]
                    if not outliers.empty:
                        validation_results["anomalies"].append({
                            "parameter": param,
                            "outlier_count": len(outliers),
                            "outlier_values": outliers[param].tolist()
                        })
                        validation_results["risk_score"] += 0.1 * len(outliers)
            
            # Check for statistical anomalies
            for column in df.select_dtypes(include=[np.number]).columns:
                if len(df) > 10:  # Need sufficient data for statistical analysis
                    z_scores = np.abs(stats.zscore(df[column].fillna(df[column].mean())))
                    extreme_outliers = df[z_scores > 3]
                    if not extreme_outliers.empty:
                        validation_results["warnings"].append(
                            f"Statistical outliers in {column}: {len(extreme_outliers)} values"
                        )
                        validation_results["risk_score"] += 0.05
            
            # Check for temporal consistency
            if "datetime" in df.columns or "date" in df.columns:
                date_col = "datetime" if "datetime" in df.columns else "date"
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    future_dates = df[df[date_col] > datetime.now() + timedelta(days=7)]
                    if not future_dates.empty:
                        validation_results["warnings"].append(
                            f"Future dates detected: {len(future_dates)} entries"
                        )
                        validation_results["risk_score"] += 0.1
                except:
                    validation_results["errors"].append("Invalid date format detected")
                    validation_results["risk_score"] += 0.2
            
            # Determine overall validation status
            if validation_results["risk_score"] > 0.5:
                validation_results["is_valid"] = False
            
            # Log validation results
            self.log_validation_results(source, validation_results)
            
        except Exception as e:
            validation_results["errors"].append(f"Validation failed: {str(e)}")
            validation_results["is_valid"] = False
            logger.error(f"Data validation error: {e}")
        
        return validation_results
    
    def analyze_user_behavior(self, user_id: str, action: str, ip_address: str = None) -> Dict:
        """Analyze user behavior for suspicious patterns"""
        behavior_analysis = {
            "is_suspicious": False,
            "risk_factors": [],
            "recommendations": []
        }
        
        try:
            current_time = datetime.now()
            
            # Rate limiting check
            user_key = f"{user_id}:{ip_address}" if ip_address else user_id
            if user_key not in self.rate_limit_store:
                self.rate_limit_store[user_key] = []
            
            # Clean old entries (last hour)
            hour_ago = current_time - timedelta(hours=1)
            self.rate_limit_store[user_key] = [
                timestamp for timestamp in self.rate_limit_store[user_key]
                if timestamp > hour_ago
            ]
            
            # Add current request
            self.rate_limit_store[user_key].append(current_time)
            
            # Check for rate limiting violation
            requests_per_hour = len(self.rate_limit_store[user_key])
            if requests_per_hour > 100:  # Adjust threshold as needed
                behavior_analysis["is_suspicious"] = True
                behavior_analysis["risk_factors"].append(
                    f"High request rate: {requests_per_hour} requests/hour"
                )
                behavior_analysis["recommendations"].append("Apply rate limiting")
            
            # Check for suspicious IP patterns
            if ip_address:
                if self.is_suspicious_ip(ip_address):
                    behavior_analysis["is_suspicious"] = True
                    behavior_analysis["risk_factors"].append(
                        f"Suspicious IP address: {ip_address}"
                    )
                    behavior_analysis["recommendations"].append("Block IP address")
            
            # Log audit trail
            self.log_user_action(user_id, action, ip_address, behavior_analysis)
            
        except Exception as e:
            logger.error(f"Behavior analysis error: {e}")
        
        return behavior_analysis
    
    def is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is from suspicious networks"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check for private/local addresses (might be suspicious in production)
            if ip.is_private or ip.is_loopback:
                return False
            
            # Add known malicious IP ranges or use threat intelligence feeds
            # This is a simplified example
            suspicious_ranges = [
                # Add known bad IP ranges here
            ]
            
            for range_str in suspicious_ranges:
                if ip in ipaddress.ip_network(range_str):
                    return True
            
            return False
        except:
            return True  # Invalid IP format is suspicious
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            return self.cipher_suite.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_data
    
    def generate_security_alert(self, threat_type: ThreatType, severity: SecurityLevel, 
                              description: str, source: str, **kwargs) -> SecurityAlert:
        """Generate security alert"""
        alert_id = hashlib.md5(
            f"{threat_type.value}{datetime.now().isoformat()}{source}".encode()
        ).hexdigest()[:12]
        
        alert = SecurityAlert(
            id=alert_id,
            timestamp=datetime.now(),
            threat_type=threat_type,
            severity=severity,
            source=source,
            description=description,
            affected_data=kwargs.get("affected_data"),
            remediation=kwargs.get("remediation", "Review and investigate"),
            user_id=kwargs.get("user_id"),
            ip_address=kwargs.get("ip_address"),
            metadata=kwargs.get("metadata", {})
        )
        
        # Store alert in database
        self.store_security_alert(alert)
        
        return alert
    
    def store_security_alert(self, alert: SecurityAlert):
        """Store security alert in database"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO security_alerts 
                        (id, timestamp, threat_type, severity, source, description, 
                         affected_data, remediation, user_id, ip_address, metadata)
                        VALUES (:id, :timestamp, :threat_type, :severity, :source, 
                                :description, :affected_data, :remediation, :user_id, 
                                :ip_address, :metadata)
                    """), {
                        "id": alert.id,
                        "timestamp": alert.timestamp,
                        "threat_type": alert.threat_type.value,
                        "severity": alert.severity.value,
                        "source": alert.source,
                        "description": alert.description,
                        "affected_data": alert.affected_data,
                        "remediation": alert.remediation,
                        "user_id": alert.user_id,
                        "ip_address": alert.ip_address,
                        "metadata": json.dumps(alert.metadata) if alert.metadata else None
                    })
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to store security alert: {e}")
    
    def log_validation_results(self, source: str, results: Dict):
        """Log data validation results"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO data_validation_log 
                        (data_source, validation_type, status, errors_found, details)
                        VALUES (:source, :type, :status, :errors, :details)
                    """), {
                        "source": source,
                        "type": "weather_data",
                        "status": "valid" if results["is_valid"] else "invalid",
                        "errors": len(results["errors"]),
                        "details": json.dumps(results)
                    })
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to log validation results: {e}")
    
    def log_user_action(self, user_id: str, action: str, ip_address: str, analysis: Dict):
        """Log user action for audit trail"""
        try:
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO security_audit_log 
                        (action, user_id, ip_address, resource, success, details)
                        VALUES (:action, :user_id, :ip_address, :resource, :success, :details)
                    """), {
                        "action": action,
                        "user_id": user_id,
                        "ip_address": ip_address,
                        "resource": "api_endpoint",
                        "success": not analysis["is_suspicious"],
                        "details": json.dumps(analysis)
                    })
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to log user action: {e}")
    
    def get_security_dashboard_data(self) -> Dict:
        """Get security dashboard data"""
        try:
            dashboard_data = {
                "alerts_24h": 0,
                "critical_alerts": 0,
                "blocked_requests": 0,
                "validation_errors": 0,
                "top_threats": [],
                "recent_alerts": []
            }
            
            if hasattr(self, 'engine'):
                with self.engine.connect() as conn:
                    # Count alerts in last 24 hours
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM security_alerts 
                        WHERE timestamp > NOW() - INTERVAL '24 hours'
                    """))
                    dashboard_data["alerts_24h"] = result.fetchone()[0]
                    
                    # Count critical alerts
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM security_alerts 
                        WHERE severity = 'critical' AND timestamp > NOW() - INTERVAL '7 days'
                    """))
                    dashboard_data["critical_alerts"] = result.fetchone()[0]
                    
                    # Get recent alerts
                    result = conn.execute(text("""
                        SELECT id, timestamp, threat_type, severity, description 
                        FROM security_alerts 
                        ORDER BY timestamp DESC LIMIT 10
                    """))
                    dashboard_data["recent_alerts"] = [
                        {
                            "id": row[0],
                            "timestamp": row[1].isoformat(),
                            "threat_type": row[2],
                            "severity": row[3],
                            "description": row[4]
                        }
                        for row in result.fetchall()
                    ]
            
            return dashboard_data
        except Exception as e:
            logger.error(f"Failed to get security dashboard data: {e}")
            return {"error": str(e)}

# Global security agent instance
security_agent_instance = None

def get_security_agent():
    """Get or create global security agent instance"""
    global security_agent_instance
    if security_agent_instance is None:
        security_agent_instance = SecurityAgent()
    return security_agent_instance

# LangChain tools for security operations
@tool("validate_weather_data", return_direct=True)
def validate_weather_data_tool(tool_input: str) -> str:
    """
    Validate weather data for security threats and anomalies.
    tool_input: JSON string with data and source information
    """
    try:
        agent = get_security_agent()
        input_data = json.loads(tool_input)
        data = input_data.get("data")
        source = input_data.get("source", "unknown")
        
        results = agent.validate_weather_data(data, source)
        return json.dumps(results, default=str)
    except Exception as e:
        return json.dumps({"error": f"Validation failed: {str(e)}"})

@tool("analyze_user_behavior", return_direct=True)
def analyze_user_behavior_tool(tool_input: str) -> str:
    """
    Analyze user behavior for suspicious patterns.
    tool_input: JSON string with user_id, action, and ip_address
    """
    try:
        agent = get_security_agent()
        input_data = json.loads(tool_input)
        
        results = agent.analyze_user_behavior(
            input_data.get("user_id"),
            input_data.get("action"),
            input_data.get("ip_address")
        )
        return json.dumps(results, default=str)
    except Exception as e:
        return json.dumps({"error": f"Behavior analysis failed: {str(e)}"})

@tool("generate_security_report", return_direct=True)
def generate_security_report_tool(tool_input: str) -> str:
    """
    Generate security status report.
    tool_input: time_range (24h, 7d, 30d)
    """
    try:
        agent = get_security_agent()
        dashboard_data = agent.get_security_dashboard_data()
        return json.dumps(dashboard_data, default=str)
    except Exception as e:
        return json.dumps({"error": f"Report generation failed: {str(e)}"})

# Security tools list
security_tools = [
    validate_weather_data_tool,
    analyze_user_behavior_tool,
    generate_security_report_tool
]

# LangGraph workflow for security agent
def validation_node(state: SecurityState) -> SecurityState:
    """Validate input data for security threats"""
    try:
        input_data = state["input_data"]
        tool_input = json.dumps({
            "data": input_data.get("data"),
            "source": input_data.get("source", "api")
        })
        
        result = validate_weather_data_tool.invoke(tool_input)
        state["validation_results"] = json.loads(result)
        
        if not state["validation_results"]["is_valid"]:
            state["risk_score"] = state["validation_results"]["risk_score"]
            
    except Exception as e:
        state["error"] = f"Validation node failed: {str(e)}"
    
    return state

def threat_analysis_node(state: SecurityState) -> SecurityState:
    """Analyze potential security threats"""
    try:
        if "user_id" in state["input_data"]:
            tool_input = json.dumps({
                "user_id": state["input_data"]["user_id"],
                "action": state["input_data"].get("action", "data_access"),
                "ip_address": state["input_data"].get("ip_address")
            })
            
            result = analyze_user_behavior_tool.invoke(tool_input)
            state["threat_analysis"] = json.loads(result)
            
    except Exception as e:
        state["error"] = f"Threat analysis node failed: {str(e)}"
    
    return state

def security_response_node(state: SecurityState) -> SecurityState:
    """Generate security response and recommendations"""
    try:
        recommendations = []
        risk_score = state.get("risk_score", 0.0)
        
        # Add behavior-based recommendations
        if state.get("threat_analysis", {}).get("is_suspicious"):
            recommendations.extend(state["threat_analysis"]["recommendations"])
            risk_score += 0.3
        
        # Add validation-based recommendations
        validation_results = state.get("validation_results", {})
        if not validation_results.get("is_valid", True):
            recommendations.append("Reject data due to validation failures")
            recommendations.append("Investigate data source integrity")
        
        if validation_results.get("anomalies"):
            recommendations.append("Review data anomalies with domain experts")
        
        # Overall risk assessment
        if risk_score > 0.7:
            recommendations.append("URGENT: Escalate to security team")
        elif risk_score > 0.4:
            recommendations.append("Monitor closely for additional threats")
        
        state["risk_score"] = risk_score
        state["recommendations"] = recommendations
        
        # Generate summary output
        state["output"] = json.dumps({
            "security_status": "HIGH_RISK" if risk_score > 0.5 else "ACCEPTABLE",
            "risk_score": risk_score,
            "validation_passed": validation_results.get("is_valid", True),
            "behavior_analysis": state.get("threat_analysis", {}),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }, default=str)
        
    except Exception as e:
        state["error"] = f"Security response node failed: {str(e)}"
    
    return state

# Create security workflow
security_workflow = StateGraph(SecurityState)

# Add nodes
security_workflow.add_node("validation", validation_node)
security_workflow.add_node("threat_analysis", threat_analysis_node)
security_workflow.add_node("security_response", security_response_node)

# Add edges
security_workflow.add_edge(START, "validation")
security_workflow.add_edge("validation", "threat_analysis")
security_workflow.add_edge("threat_analysis", "security_response")
security_workflow.add_edge("security_response", END)

# Compile security agent
security_app = security_workflow.compile()

def run_security_agent(input_data: Dict) -> str:
    """
    Run the security agent with input data
    
    Args:
        input_data: Dictionary containing data to analyze and context
        
    Returns:
        str: JSON string with security analysis results
    """
    try:
        initial_state = SecurityState(
            input_data=input_data,
            validation_results=None,
            threat_analysis=None,
            security_alerts=None,
            risk_score=None,
            recommendations=None,
            output="",
            error=None
        )
        
        result = security_app.invoke(initial_state)
        return result["output"]
        
    except Exception as e:
        return json.dumps({
            "error": f"Security agent failed: {str(e)}",
            "security_status": "ERROR",
            "timestamp": datetime.now().isoformat()
        }, default=str)

# Test function
if __name__ == "__main__":
    # Test security agent
    test_data = {
        "data": {
            "temperature": 25.5,
            "humidity": 68.2,
            "pressure": 1013.2
        },
        "source": "weather_api",
        "user_id": "test_user",
        "action": "data_upload",
        "ip_address": "192.168.1.100"
    }
    
    print("🔒 Testing Security Agent...")
    result = run_security_agent(test_data)
    print(f"Security Analysis Result:\n{result}")