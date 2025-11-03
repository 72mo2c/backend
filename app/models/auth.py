from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class AuthSession(BaseModel):
    __tablename__ = "auth_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuthSession(id={self.id}, user_id={self.user_id})>"


class PasswordResetToken(BaseModel):
    __tablename__ = "password_reset_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"


class EmailVerificationToken(BaseModel):
    __tablename__ = "email_verification_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False)
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id})>"
