from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
    RegistrationRequest, RegistrationResponse, PasswordResetResponse,
    LogoutResponse
)
from app.core.security import decode_access_token
from app.api.deps import get_current_user, get_current_active_user
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """تسجيل الدخول"""
    auth_service = AuthService(db)
    
    # المصادقة
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة"
        )
    
    # إنشاء رموز الوصول
    token_data = auth_service.create_access_refresh_tokens(user)
    
    # تحديث آخر تسجيل دخول
    auth_service.update_last_login(user.id)
    
    return LoginResponse(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"],
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """تحديث رمز الوصول"""
    auth_service = AuthService(db)
    
    token_data = auth_service.refresh_user_token(refresh_data.refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز التحديث غير صالح"
        )
    
    return RefreshTokenResponse(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"]
    )


@router.post("/logout")
async def logout():
    """تسجيل الخروج"""
    # في التطبيق الحقيقي، تحتاج لحفظ الرموز في قاعدة البيانات وتثبيتها
    return {"message": "تم تسجيل الخروج بنجاح"}


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """تغيير كلمة المرور"""
    auth_service = AuthService(db)
    
    try:
        auth_service.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        return {"message": "تم تغيير كلمة المرور بنجاح"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/register", response_model=RegistrationResponse)
async def register(
    user_data: RegistrationRequest,
    db: Session = Depends(get_db)
):
    """تسجيل مستخدم جديد"""
    auth_service = AuthService(db)
    
    # تحقق من قوة كلمة المرور
    is_strong, errors = auth_service.validate_password_strength(user_data.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"كلمة المرور غير قوية: {'; '.join(errors)}"
        )
    
    try:
        user = auth_service.create_user(user_data.dict())
        
        return RegistrationResponse(
            message="تم إنشاء الحساب بنجاح",
            user_id=user.id,
            username=user.username,
            email=user.email
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """طلب إعادة تعيين كلمة المرور"""
    auth_service = AuthService(db)
    
    # إنشاء رمز إعادة التعيين
    reset_token = auth_service.generate_reset_token(reset_data.email)
    
    # في التطبيق الحقيقي، يجب إرسال البريد الإلكتروني هنا
    # للتبسيط، سنعيد الرمز في الاستجابة (ليس آمن في الإنتاج)
    
    return PasswordResetResponse(
        message="إذا كان البريد الإلكتروني مسجل لدينا، سيتم إرسال رمز إعادة التعيين قريباً"
    )


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """إعادة تعيين كلمة المرور باستخدام الرمز"""
    auth_service = AuthService(db)
    
    try:
        auth_service.reset_password(reset_data.token, reset_data.new_password)
        return {"message": "تم إعادة تعيين كلمة المرور بنجاح"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """تسجيل الخروج"""
    # في التطبيق الحقيقي، يمكن حفظ الرموز في قاعدة البيانات وتثبيتها
    # أو استخدام Redis لحفظ الرموز المنتهية الصلاحية
    
    # تحديث آخر نشاط للمستخدم
    from datetime import datetime
    current_user.last_login = datetime.utcnow()
    db.commit()
    
    return LogoutResponse(
        message="تم تسجيل الخروج بنجاح"
    )
