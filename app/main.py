import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.database import get_db, engine
from app.models.base import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting up Multi-Tenant SaaS Backend...")
    
    try:
        # Create tables on startup
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Log environment info
        logger.info(f"🌍 Environment: {settings.environment}")
        logger.info(f"🔧 Debug Mode: {settings.debug}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    finally:
        logger.info("🛑 Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Multi-Tenant SaaS Backend",
    description="نظام SaaS متعدد المستأجرين مع FastAPI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.environment == "production" else None,
    redoc_url="/redoc" if not settings.environment == "production" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API routes
from app.api import auth, users, tenants, roles, subscriptions, branches

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(branches.router, prefix="/api/branches", tags=["Branches"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "مرحباً بك في نظام SaaS متعدد المستأجرين",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs" if settings.environment != "production" else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test database connection
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.environment,
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service Unavailable")


@app.get("/ready")
async def readiness_check():
    """Readiness check for Railway"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.debug
    )
