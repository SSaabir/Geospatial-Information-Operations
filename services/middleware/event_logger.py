from typing import Optional, Dict, Any
import time
import logging
from sqlalchemy import text

from db_config import db_config
from security.jwt_handler import jwt_handler

logger = logging.getLogger(__name__)


def _get_engine():
    return db_config.get_engine()


def log_api_access(
    endpoint: str,
    method: str,
    user_id: Optional[int],
    ip_address: Optional[str],
    user_agent: Optional[str],
    response_code: int,
    response_time: float,
    request_size: Optional[int] = None,
    response_size: Optional[int] = None,
    threat_score: float = 0.0,
):
    """Insert a row into api_access_log (best-effort)."""
    try:
        engine = _get_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO api_access_log (
                        endpoint, method, user_id, ip_address, user_agent,
                        response_code, response_time, request_size, response_size, threat_score
                    ) VALUES (:endpoint, :method, :user_id, :ip_address, :user_agent,
                              :response_code, :response_time, :request_size, :response_size, :threat_score)
                    """
                ),
                {
                    "endpoint": endpoint,
                    "method": method,
                    "user_id": str(user_id) if user_id is not None else None,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "response_code": response_code,
                    "response_time": response_time,
                    "request_size": request_size,
                    "response_size": response_size,
                    "threat_score": threat_score,
                },
            )
    except Exception as e:
        logger.debug(f"Failed to log api access: {e}")


def log_auth_event(
    event_type: str,
    user_id: Optional[int],
    success: bool,
    ip_address: Optional[str] = None,
    failure_reason: Optional[str] = None,
    session_id: Optional[str] = None,
    user_agent: Optional[str] = None,
    geolocation: Optional[Dict[str, Any]] = None,
):
    """Insert a row into auth_events for auditability."""
    try:
        engine = _get_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO auth_events (
                        event_type, user_id, ip_address, success, failure_reason, session_id, user_agent, geolocation
                    ) VALUES (:event_type, :user_id, :ip_address, :success, :failure_reason, :session_id, :user_agent, :geolocation)
                    """
                ),
                {
                    "event_type": event_type,
                    "user_id": str(user_id) if user_id is not None else None,
                    "ip_address": ip_address,
                    "success": success,
                    "failure_reason": failure_reason,
                    "session_id": session_id,
                    "user_agent": user_agent,
                    "geolocation": json_or_none(geolocation),
                },
            )
    except Exception as e:
        logger.debug(f"Failed to log auth event: {e}")


def json_or_none(obj):
    try:
        import json
        return json.dumps(obj) if obj is not None else None
    except Exception:
        return None


def increment_usage_metrics(user_id: int, api_calls: int = 1, reports_generated: int = 0, data_downloads: int = 0):
    """Increment or create the usage_metrics row for a user."""
    try:
        engine = _get_engine()
        with engine.begin() as conn:
            # Try update first
            result = conn.execute(
                text(
                    "UPDATE usage_metrics SET api_calls = api_calls + :api_calls, reports_generated = reports_generated + :reports_generated, data_downloads = data_downloads + :data_downloads, updated_at = CURRENT_TIMESTAMP WHERE user_id = :user_id"
                ),
                {
                    "api_calls": api_calls,
                    "reports_generated": reports_generated,
                    "data_downloads": data_downloads,
                    "user_id": user_id,
                },
            )
            if result.rowcount == 0:
                conn.execute(
                    text(
                        "INSERT INTO usage_metrics (user_id, api_calls, reports_generated, data_downloads) VALUES (:user_id, :api_calls, :reports_generated, :data_downloads)"
                    ),
                    {
                        "user_id": user_id,
                        "api_calls": api_calls,
                        "reports_generated": reports_generated,
                        "data_downloads": data_downloads,
                    },
                )
    except Exception as e:
        logger.debug(f"Failed to increment usage metrics: {e}")
