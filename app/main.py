import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import get_db
from app.database import engine
from app.models.base import Base

# إعداد logging للإنتاج
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 تشغيل خادم SaaS Backend...")
    try:
        # إنشاء الجداول
        Base.metadata.create_all(bind=engine)
        logger.info("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء الجداول: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 إغلاق خادم SaaS Backend...")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Multi-Tenant SaaS Backend",
    description="نظام متعدد المستأجرين SaaS - جاهز للإنتاج",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # تعطيل docs في الإنتاج
    redoc_url="/redoc" if settings.DEBUG else None,  # تعطيل redoc في الإنتاج
    lifespan=lifespan
)

# إعداد CORS للإنتاج
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# تضمين API routes
from app.api import auth, users, tenants, roles, subscriptions, branches

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(branches.router, prefix="/api/branches", tags=["Branches"])

# الـ endpoints الأساسية
@app.get("/")
async def root():
    return {
        "message": "مرحباً بك في نظام SaaS متعدد المستأجرين",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint لـ Render"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "timestamp": "2025-11-03T22:27:35Z"
    }

# معالجة الأخطاء العامة
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"خطأ غير متوقع: {str(exc)}", exc_info=True)
    return {
        "error": "خطأ داخلي في الخادم",
        "detail": "حدث خطأ غير متوقع، يرجى المحاولة لاحقاً"
    }

# للتوافق مع Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(settings.PORT), 
        reload=False  # تعطيل reload في الإنتاج
    )