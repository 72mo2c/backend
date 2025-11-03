from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import secrets
import string
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.models.user import User
from app.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """خدمة المصادقة الكاملة"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: dict) -> User:
        """إنشاء مستخدم جديد"""
        # التحقق من عدم وجود اسم المستخدم
        existing_user = self.db.query(User).filter(
            or_(User.username == user_data['username'], User.email == user_data['email'])
        ).first()
        
        if existing_user:
            if existing_user.username == user_data['username']:
                raise ValueError("اسم المستخدم موجود بالفعل")
            else:
                raise ValueError("البريد الإلكتروني موجود بالفعل")
        
        # إنشاء المستخدم
        hashed_password = get_password_hash(user_data['password'])
        
        db_user = User(
            username=user_data['username'],
            email=user_data['email'],
            hashed_password=hashed_password,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data.get('phone'),
            tenant_id=user_data.get('tenant_id'),
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """مصادقة المستخدم"""
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def create_access_refresh_tokens(self, user: User) -> dict:
        """إنشاء رموز الوصول والتحديث"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": user.id, "tenant_id": user.tenant_id},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user.id, "tenant_id": user.tenant_id},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """تغيير كلمة المرور"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("المستخدم غير موجود")
        
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("كلمة المرور الحالية غير صحيحة")
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def generate_reset_token(self, email: str) -> str:
        """إنشاء رمز إعادة تعيين كلمة المرور"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # لأسباب أمنية، لا نكشف أن البريد الإلكتروني غير موجود
            return ""
        
        # إنشاء رمز عشوائي
        reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # إنشاء JWT token مع expiry
        expire = datetime.utcnow() + timedelta(hours=1)  # ينتهي خلال ساعة
        to_encode = {
            "sub": user.id,
            "email": user.email,
            "exp": expire,
            "type": "password_reset"
        }
        reset_token_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return reset_token_jwt
    
    def verify_reset_token(self, token: str) -> Optional[User]:
        """التحقق من رمز إعادة التعيين"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            user_id: int = payload.get("sub")
            email: str = payload.get("email")
            token_type: str = payload.get("type")
            
            if token_type != "password_reset":
                return None
                
            if user_id is None or email is None:
                return None
                
        except JWTError:
            return None
        
        user = self.db.query(User).filter(
            and_(User.id == user_id, User.email == email)
        ).first()
        
        return user
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """إعادة تعيين كلمة المرور باستخدام الرمز"""
        user = self.verify_reset_token(token)
        
        if not user:
            raise ValueError("رمز إعادة التعيين غير صالح أو منتهي الصلاحية")
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def refresh_user_token(self, refresh_token: str) -> Optional[dict]:
        """تجديد رمز المستخدم"""
        from app.core.security import decode_access_token
        
        try:
            payload = decode_access_token(refresh_token)
            user_id: int = payload.get("sub")
            
            if user_id is None:
                return None
                
        except Exception:
            return None
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            return None
        
        return self.create_access_refresh_tokens(user)
    
    def update_last_login(self, user_id: int):
        """تحديث آخر تسجيل دخول"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
    
    def validate_password_strength(self, password: str) -> tuple[bool, list[str]]:
        """تحقق من قوة كلمة المرور"""
        errors = []
        
        if len(password) < 8:
            errors.append("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
        
        if not any(c.isupper() for c in password):
            errors.append("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
        
        if not any(c.islower() for c in password):
            errors.append("كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل")
        
        if not any(c.isdigit() for c in password):
            errors.append("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
        
        return len(errors) == 0, errors