from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/saas_db"
    
    # Security
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    algorithm: str = "HS256"
    
    # Redis (Optional for Railway)
    redis_url: Optional[str] = None
    
    # Email (للتطوير المستقبلي)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    allowed_origins: List[str] = ["*"]
    
    # API Configuration
    api_v1_str: str = "/api"
    
    # Railway specific settings
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    def get_database_url(self) -> str:
        """Parse Railway's DATABASE_URL if available"""
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        
        # Fallback to local database
        return self.database_url
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set default allowed origins based on environment
        if self.is_production:
            self.allowed_origins = [
                "https://your-domain.com",
                "https://www.your-domain.com",
                # Add your production domains here
            ]
        else:
            self.allowed_origins = [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:8080"
            ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
