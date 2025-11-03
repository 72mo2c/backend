from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import get_db
from app.config import settings
from app.core.security import decode_access_token
from app.models.user import User
from app.models.tenant import Tenant


security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="لم يتم التحقق من صحة بيانات الاعتماد",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token.credentials)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="تم إيقاف حساب المستخدم")
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, 
            detail="ليس لديك صلاحيات للوصول لهذا المورد"
        )
    return current_user


def get_current_tenant(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)) -> Tenant:
    """Get current tenant from token"""
    try:
        payload = decode_access_token(token.credentials)
        tenant_id: int = payload.get("tenant_id")
        if tenant_id is None:
            raise HTTPException(status_code=403, detail="لم يتم العثور على معلومات المستأجر")
    except JWTError:
        raise HTTPException(status_code=403, detail="رمز غير صالح")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=403, detail="المستأجر غير موجود")
    
    return tenant
