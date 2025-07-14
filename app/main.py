from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import logging
import time

from .core.config import settings
from .core.database import create_tables
from .core.cache import get_cache
from .api import auth_router, oauth_router, applications_router, admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - {process_time:.4f}s"
    )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Static directory doesn't exist, create it or skip mounting
    logger.warning("Static directory not found, skipping static file mounting")

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(oauth_router, prefix="/oauth")
app.include_router(applications_router, prefix="/api")
app.include_router(admin_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from .core.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                db_status = "healthy"
            else:
                db_status = "unhealthy"
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    try:
        # Check cache connection
        cache = get_cache()
        cache.ping()
        cache_status = "healthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        cache_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy",
        "database": db_status,
        "cache": cache_status,
        "version": settings.app_version
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "description": settings.app_description,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation not available in production",
        "health": "/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    # Test cache connection
    try:
        cache = get_cache()
        cache.ping()
        logger.info("Cache connection established")
    except Exception as e:
        logger.error(f"Failed to connect to cache: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )