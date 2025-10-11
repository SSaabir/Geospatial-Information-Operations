import logging
import sys
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
import time

logger = logging.getLogger(__name__)

class ErrorDetail:
    """Class to format error details consistently"""
    def __init__(self, error: Exception, request: Optional[Request] = None, error_id: Optional[str] = None):
        self.error = error
        self.request = request
        self.error_id = error_id or time.strftime('%Y%m%d%H%M%S')
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error details to a dictionary format"""
        error_dict = {
            "type": self.error.__class__.__name__,
            "message": str(self.error),
            "error_id": self.error_id,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if self.request:
            error_dict.update({
                "path": str(self.request.url.path),
                "method": self.request.method,
                "client_host": str(self.request.client.host if self.request.client else "unknown"),
            })
            
        return error_dict

def log_error_details(error: Exception, request: Optional[Request] = None, error_id: Optional[str] = None) -> None:
    """Log detailed error information"""
    error_detail = ErrorDetail(error, request, error_id)
    error_info = error_detail.to_dict()
    
    # Add stack trace for debugging
    stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    error_info["stack_trace"] = stack_trace
    
    # Log basic error info at ERROR level
    logger.error(f"Error {error_info['error_id']}: {error_info['type']} - {error_info['message']}")
    
    # Log detailed debug info at DEBUG level
    logger.debug(f"Detailed error information for {error_info['error_id']}:", 
                extra={"error_details": error_info})
    
    # If in development, print stack trace to stderr
    if logger.level <= logging.DEBUG:
        print(stack_trace, file=sys.stderr)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for capturing unhandled exceptions"""
    error_id = time.strftime('%Y%m%d%H%M%S')
    
    # Log the error with full context
    log_error_details(exc, request, error_id)
    
    # Return a sanitized response to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "type": "internal_server_error",
            "error_id": error_id,
            "path": request.url.path,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

def setup_error_handlers(app):
    """Set up global error handlers for the application"""
    @app.middleware("http")
    async def error_handling_middleware(request: Request, call_next):
        try:
            response = await call_next(request)
            
            # If response has error status code, log it
            if response.status_code >= 400:
                error_detail = {
                    "status_code": response.status_code,
                    "path": request.url.path,
                    "method": request.method,
                }
                logger.error(f"HTTP {response.status_code} error: {error_detail}")
            
            return response
            
        except Exception as exc:
            # Don't catch HTTPException - let FastAPI handle it
            if isinstance(exc, HTTPException):
                raise
            
            return await global_exception_handler(request, exc)