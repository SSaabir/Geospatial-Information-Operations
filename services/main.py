from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
import time
import sqlalchemy.exc
from pathlib import Path
from middleware.event_logger import log_api_access
# Import modules
from models.user import Base, UserDB
from api.auth import auth_router
from api.orchestrator_api import orchestrator_router
from api.security_api import security_router
from api.analytics_api import analytics_router
from api.ai_ethics_api import ai_ethics_router
from api.billing_api import billing_router
from db_config import DatabaseConfig
from db_seed import create_tables_and_seed
from security.auth_middleware import AuthenticationError, AuthorizationError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
db_config = DatabaseConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Geospatial Information Operations API")
    
    # Create database tables
    try:
        engine = db_config.get_engine()
        # Create application tables defined by SQLAlchemy models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        # Create audit/payment tables and seed sample data (idempotent)
        try:
            create_tables_and_seed()
        except Exception as e:
            logger.exception("db_seed failed: %s", e)
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Geospatial Information Operations API")

# Create FastAPI application
app = FastAPI(
    title="Geospatial Information Operations API",
    description="REST API for climate data analysis, trend analysis, and geospatial operations with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Set up global error handlers
from middleware.error_handlers import setup_error_handlers
setup_error_handlers(app)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted host middleware (optional, for production)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
    )

# Include routers
app.include_router(auth_router)
app.include_router(orchestrator_router)
app.include_router(security_router)
app.include_router(ai_ethics_router)
app.include_router(analytics_router)
app.include_router(billing_router)

# Mount static files for visualizations
visualizations_dir = Path(__file__).parent / "visualizations"
visualizations_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist

# Mount the visualizations directory
app.mount("/visualizations", StaticFiles(directory=str(visualizations_dir)), name="visualizations")
logger.info(f"Mounted visualizations directory: {visualizations_dir}")


# Custom exception handlers
@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors"""
    logger.error(f"Authentication error: {exc.message} - Request: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "type": "authentication_error",
            "path": request.url.path,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handle authorization errors"""
    logger.error(f"Authorization error: {exc.message} - Request: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "type": "authorization_error",
            "path": request.url.path,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail} - Request: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error",
            "path": request.url.path,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    error_id = time.strftime('%Y%m%d%H%M%S')
    logger.exception(f"Unhandled error {error_id}: {str(exc)} - Request: {request.method} {request.url.path}")
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

# Database related exception handlers
@app.exception_handler(sqlalchemy.exc.SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: sqlalchemy.exc.SQLAlchemyError):
    """Handle database related errors"""
    error_id = time.strftime('%Y%m%d%H%M%S')
    logger.error(f"Database error {error_id}: {str(exc)} - Request: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "A database error occurred",
            "type": "database_error",
            "error_id": error_id,
            "path": request.url.path,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Geospatial Information Operations API is running",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Geospatial Information Operations API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Simple request logging middleware (best-effort, non-blocking)
@app.middleware("http")
async def request_event_logger(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        # If underlying call throws, log and re-raise
        status_code = 500
        raise
    finally:
        duration = time.time() - start
        try:
            user_id = None
            # Attempt to get user info from Authorization header (best-effort)
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                token = auth_header.split(" ", 1)[1]
                payload = None
                try:
                    payload = __import__('security.jwt_handler', fromlist=['jwt_handler']).jwt_handler.verify_token(token)
                except Exception as e:
                    logger.debug("jwt_handler.verify_token failed: %s", e)
                    payload = None
                if payload and 'user_id' in payload:
                    try:
                        user_id = int(payload.get('user_id'))
                    except Exception as e:
                        logger.debug("Failed to parse user_id from token payload: %s", e)
                        user_id = None

            # Get request size from content-length header or default to 0
            request_size = int(request.headers.get('content-length', 0))
            # For now, we'll set a default threat score of 0
            # In production, you would want to calculate this based on security rules
            threat_score = 0.0
            
            log_api_access(
                endpoint=str(request.url.path),
                method=request.method,
                user_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get('user-agent', ''),
                response_code=status_code,
                response_time=duration,
                request_size=request_size,
                response_size=0,  # We can't get response size easily in middleware
                threat_score=threat_score
            )
        except Exception:
            # Log failures in the logging/auditing path so we can detect them
            logger.exception("Failed to write api access log (non-fatal)")
    return response



# Run the application
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        debug=debug,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )