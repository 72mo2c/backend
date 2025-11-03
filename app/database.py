"""
إعدادات قاعدة البيانات PostgreSQL - SQLAlchemy Configuration
"""

import os
from typing import Generator, Optional
from urllib.parse import quote

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError, OperationalError
import logging

# إعداد قاعدة النموذج الأساسية
Base = declarative_base()

# إعداد السجلات
logger = logging.getLogger(__name__)

# إعدادات الاتصال بقاعدة البيانات
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/bero_system"
)

# تنظيف وتحضير URL
def get_database_url() -> str:
    """
    الحصول على رابط قاعدة البيانات مع التشفير الآمن
    """
    db_url = DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # تشفير كلمة المرور إذا لم تكن مشفرة
    if "@" in db_url and "postgresql://" in db_url:
        parts = db_url.split("@")
        user_pass = parts[0].split("://")
        if len(user_pass) == 2:
            user_part = user_pass[1]
            if ":" in user_part and not user_pass[0].endswith(":"):
                user, password = user_part.split(":", 1)
                encoded_password = quote(password, safe='')
                db_url = f"{user_pass[0]}://{user}:{encoded_password}@{parts[1]}"
    
    return db_url

# إعداد SQLAlchemy Engine
def create_engine_config():
    """
    إعداد محرك SQLAlchemy مع إعدادات الاتصال المجمعة
    """
    database_url = get_database_url()
    
    engine = create_engine(
        database_url,
        # إعدادات الاتصال المجمعة
        poolclass=QueuePool,
        pool_size=20,              # عدد الاتصالات النشطة
        max_overflow=30,           # الاتصالات الزائدة
        pool_pre_ping=True,        # فحص الاتصال قبل الاستخدام
        pool_recycle=3600,         # إعادة تدوير الاتصال كل ساعة
        pool_timeout=30,           # مهلة الانتظار للاتصال
        
        # إعدادات الأداء
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        echo_pool=os.getenv("SQL_ECHO_POOL", "false").lower() == "true",
        
        # إعدادات PostgreSQL المحددة
        connect_args={
            "application_name": "bero_system_api",
            "connect_timeout": 10,
            "options": "-c timezone=Asia/Riyadh"
        },
        
        # إعدادات التاريج
        future=True  # استخدام SQLAlchemy 2.0 style
    )
    
    return engine

# إنشاء محرك SQLAlchemy
engine = create_engine_config()

# إعداد Session Maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# إعدادات التحديث التلقائي للنماذج
def get_tenant_from_session() -> Optional[str]:
    """
    الحصول على tenant_id من سياق الجلسة
    """
    return getattr(get_current_session(), "tenant_id", None)

def get_current_session() -> Session:
    """
    الحصول على الجلسة الحالية من سياق SQLAlchemy
    """
    try:
        from sqlalchemy.orm import contextmanager
        return SessionLocal.get_context()
    except:
        return None

def set_tenant_in_session(session: Session, tenant_id: str):
    """
    تعيين tenant_id في سياق الجلسة
    """
    session.info["tenant_id"] = tenant_id

# معالج أخطاء الاتصال
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    تعيين إعدادات PostgreSQL عند الاتصال
    """
    cursor = dbapi_connection.cursor()
    
    # إعداد المنطقة الزمنية
    cursor.execute("SET timezone = 'Asia/Riyadh'")
    
    # تحسين الأداء
    cursor.execute("SET shared_preload_libraries = 'pg_stat_statements'")
    
    # إعدادات الجلسة
    cursor.execute("SET session_replication_role = 'origin'")
    
    cursor.close()
    logger.info("تم إعداد إعدادات PostgreSQL بنجاح")

# معالج أخطاء الاتصال
def handle_db_connection():
    """
    معالج إعادة الاتصال عند انقطاع الاتصال
    """
    def _ping_connection(connection, connection_record, connection_proxy):
        """
        فحص الاتصال وإعادة الاتصال إذا لزم الأمر
        """
        try:
            # تنفيذ استعلام بسيط لفحص الاتصال
            connection.execute("SELECT 1")
        except (DisconnectionError, OperationalError):
            logger.warning("تم اكتشاف انقطاع الاتصال، إعادة الاتصال...")
            connection_proxy.invalidate()
            raise
    
    event.listen(engine, "checkout", _ping_connection)

# تطبيق معالج الأخطاء
handle_db_connection()

# دوال إدارة الجلسة
def get_db() -> Generator[Session, None, None]:
    """
    دالة مساعدة للحصول على جلسة قاعدة البيانات
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"خطأ في الجلسة: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_session() -> Session:
    """
    إنشاء جلسة قاعدة بيانات جديدة
    """
    return SessionLocal()

def create_tables():
    """
    إنشاء جميع الجداول
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("تم إنشاء جميع الجداول بنجاح")
    except Exception as e:
        logger.error(f"فشل في إنشاء الجداول: {e}")
        raise

def drop_tables():
    """
    حذف جميع الجداول (للاختبار فقط)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("تم حذف جميع الجداول بنجاح")
    except Exception as e:
        logger.error(f"فشل في حذف الجداول: {e}")
        raise

# دوال الصحة والأداء
def health_check() -> dict:
    """
    فحص صحة قاعدة البيانات
    """
    try:
        with engine.connect() as conn:
            # فحص الاتصال
            result = conn.execute("SELECT 1 as test")
            result.fetchone()
            
            # فحص إصدار PostgreSQL
            version_result = conn.execute("SELECT version() as version")
            version = version_result.fetchone()[0]
            
            return {
                "status": "healthy",
                "database_version": version,
                "connection_pool": {
                    "pool_size": engine.pool.size(),
                    "checked_in": engine.pool.checkedin(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                    "invalid": engine.pool.invalid()
                }
            }
    except Exception as e:
        logger.error(f"فشل في فحص الصحة: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# دوال الإحصائيات
def get_database_stats() -> dict:
    """
    إحصائيات قاعدة البيانات
    """
    try:
        with engine.connect() as conn:
            stats_query = """
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_analyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                LIMIT 20;
            """
            result = conn.execute(stats_query)
            
            stats = []
            for row in result:
                stats.append({
                    "schema": row[0],
                    "table": row[1],
                    "inserts": row[2],
                    "updates": row[3],
                    "deletes": row[4],
                    "live_rows": row[5],
                    "dead_rows": row[6],
                    "last_vacuum": row[7],
                    "last_analyze": row[8]
                })
            
            return {
                "table_stats": stats
            }
    except Exception as e:
        logger.error(f"فشل في جلب الإحصائيات: {e}")
        return {"error": str(e)}

# إعدادات البيئة للنماذج
MODEL_META_OPTIONS = {
    "timezone": "Asia/Riyadh"
}

# متغيرات البيئة المخصصة
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    logger.debug("تم تفعيل وضع التطوير")