from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class RegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    tenant_id: Optional[int] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('اسم المستخدم يجب أن يحتوي على أحرف وأرقام فقط')
        if len(v) < 3:
            raise ValueError('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        return v


class RegistrationResponse(BaseModel):
    message: str
    user_id: int
    username: str
    email: str


class PasswordResetResponse(BaseModel):
    message: str


class LogoutResponse(BaseModel):
    message: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    tenant_id: Optional[int] = None
