import logging
from typing import Optional, Dict, Any, Union
import time
import traceback
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db_config import get_database_engine as get_engine
from security.jwt_handler import jwt_handler

logger = logging.getLogger(__name__)

class EventLoggerError(Exception):
    """Base exception for event logger errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class DatabaseLogError(EventLoggerError):
    """Raised when database logging fails"""
    pass

def log_error(error: Union[str, Exception], context: Dict[str, Any]) -> None:
    """
    Enhanced error logging with context and stack trace
    """
    error_message = str(error)
    stack_trace = None
    
    if isinstance(error, Exception):
        stack_trace = ''.join(traceback.format_tb(error.__traceback__))
    
    error_details = {
        'error_message': error_message,
        'error_type': type(error).__name__ if isinstance(error, Exception) else 'str',
        'stack_trace': stack_trace,
        'context': context,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    logger.error(f"Error occurred: {error_message}")
    logger.debug(f"Error details: {error_details}")

def log_api_access(endpoint: str, method: str, user_id: Optional[int], ip_address: str, user_agent: str, 
                  response_code: int, response_time: float, request_size: int, response_size: int, threat_score: float):
    """Insert a row into api_access_log with enhanced error handling."""
    engine = get_engine()
    context = {
        'endpoint': endpoint,
        'method': method,
        'user_id': user_id,
        'ip_address': ip_address,
        'response_code': response_code
    }
    
    try:
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
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "response_code": response_code,
                    "response_time": response_time,
                    "request_size": request_size,
                    "response_size": response_size,
                    "threat_score": threat_score,
                }
            )
    except SQLAlchemyError as e:
        log_error(e, context)
        raise DatabaseLogError(f"Failed to log API access: {str(e)}", e)
    except Exception as e:
        log_error(e, context)
        raise EventLoggerError(f"Unexpected error logging API access: {str(e)}", e)

def log_auth_event(event_type: str, user_id: Optional[int], ip_address: str, success: bool, 
                  failure_reason: Optional[str] = None, session_id: Optional[str] = None, 
                  user_agent: Optional[str] = None, geolocation: Optional[str] = None):
    """Insert a row into auth_events with enhanced error handling."""
    engine = get_engine()
    context = {
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        'success': success,
        'session_id': session_id
    }
    
    try:
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
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "success": success,
                    "failure_reason": failure_reason,
                    "session_id": session_id,
                    "user_agent": user_agent,
                    "geolocation": geolocation,
                }
            )
    except SQLAlchemyError as e:
        log_error(e, context)
        raise DatabaseLogError(f"Failed to log authentication event: {str(e)}", e)
    except Exception as e:
        log_error(e, context)
        raise EventLoggerError(f"Unexpected error logging authentication event: {str(e)}", e)

def increment_usage_metrics(user_id: int, api_calls: int = 0, reports_generated: int = 0, data_downloads: int = 0):
    """Increment or create the usage_metrics row for a user with enhanced error handling."""
    engine = get_engine()
    context = {
        'user_id': user_id,
        'api_calls': api_calls,
        'reports_generated': reports_generated,
        'data_downloads': data_downloads
    }
    
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    UPDATE usage_metrics 
                    SET api_calls = api_calls + :api_calls, 
                        reports_generated = reports_generated + :reports_generated, 
                        data_downloads = data_downloads + :data_downloads, 
                        updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                    "api_calls": api_calls,
                    "reports_generated": reports_generated,
                    "data_downloads": data_downloads,
                }
            )
            if result.rowcount == 0:
                conn.execute(
                    text(
                        """
                        INSERT INTO usage_metrics (user_id, api_calls, reports_generated, data_downloads) 
                        VALUES (:user_id, :api_calls, :reports_generated, :data_downloads)
                        """
                    ),
                    {
                        "user_id": user_id,
                        "api_calls": api_calls,
                        "reports_generated": reports_generated,
                        "data_downloads": data_downloads,
                    }
                )
    except SQLAlchemyError as e:
        log_error(e, context)
        raise DatabaseLogError(f"Failed to increment usage metrics: {str(e)}", e)
    except Exception as e:
        log_error(e, context)
        raise EventLoggerError(f"Unexpected error incrementing usage metrics: {str(e)}", e)