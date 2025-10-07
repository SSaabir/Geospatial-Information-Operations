from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
import time

# Import modules
from models.user import Base, UserDB
from api.auth import auth_router
from api.orchestrator_api import orchestrator_router
from api.security_api import security_router
from api.analytics_api import analytics_router
from api.marketplace_api import marketplace_router
from api.ai_ethics_api import ai_ethics_router
from api.billing_api import billing_router
from api.payments_api import payments_router, start_payment_expiry_worker, db_config as payments_db_config
from db_config import DatabaseConfig
from security.auth_middleware import AuthenticationError, AuthorizationError
from middleware.event_logger import log_api_access
from fastapi import Request

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
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    # Start payment expiry worker
    try:
        start_payment_expiry_worker(payments_db_config)
    except Exception as e:
        logger.error(f"Failed to start payment expiry worker: {e}")
    
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
app.include_router(marketplace_router)
app.include_router(billing_router)
app.include_router(payments_router)


# Custom exception handlers
@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request, exc: AuthenticationError):
    """Handle authentication errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request, exc: AuthorizationError):
    """Handle authorization errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
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
                except Exception:
                    payload = None
                if payload and 'user_id' in payload:
                    try:
                        user_id = int(payload.get('user_id'))
                    except Exception:
                        user_id = None

            log_api_access(
                endpoint=str(request.url.path),
                method=request.method,
                user_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get('user-agent'),
                response_code=status_code,
                response_time=duration,
            )
        except Exception:
            pass
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