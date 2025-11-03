from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import get_db
from app.database import engine
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Multi-Tenant SaaS Backend",
    description="نظام متعدد المستأجرين SaaS",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "مرحباً بك في نظام SaaS متعدد المستأجرين"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}