from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """الحصول على مستخدم بالمعرف"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """الحصول على مستخدم بالإيميل"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """الحصول على مستخدم باسم المستخدم"""
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user_data: UserCreate, tenant_id: Optional[int] = None) -> User:
        """إنشاء مستخدم جديد"""
        # التحقق من عدم وجود المستخدم مسبقاً
        if self.get_user_by_email(user_data.email):
            raise ValueError("المستخدم موجود بالفعل بهذا الإيميل")
        
        if self.get_user_by_username(user_data.username):
            raise ValueError("المستخدم موجود بالفعل بهذا الاسم")

        # إنشاء المستخدم الجديد
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            hashed_password=get_password_hash(user_data.password),
            tenant_id=tenant_id
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """تحديث بيانات المستخدم"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        # تحديث البيانات
        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "password" and value:
                setattr(db_user, "hashed_password", get_password_hash(value))
            elif field != "password":
                setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def delete_user(self, user_id: int) -> bool:
        """حذف المستخدم"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """مصادقة المستخدم"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    def get_users_by_tenant(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """الحصول على مستخدمي الشركة"""
        return (self.db.query(User)
                .filter(User.tenant_id == tenant_id)
                .offset(skip)
                .limit(limit)
                .all())

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """الحصول على جميع المستخدمين (للمدراء فقط)"""
        return (self.db.query(User)
                .offset(skip)
                .limit(limit)
                .all())

    def assign_user_to_tenant(self, user_id: int, tenant_id: int) -> bool:
        """تعيين مستخدم لشركة"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.tenant_id = tenant_id
        self.db.commit()
        
        return True

    def remove_user_from_tenant(self, user_id: int) -> bool:
        """إزالة مستخدم من الشركة"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.tenant_id = None
        self.db.commit()
        
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """إلغاء تفعيل المستخدم"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        self.db.commit()
        
        return True

    def activate_user(self, user_id: int) -> bool:
        """تفعيل المستخدم"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = True
        self.db.commit()
        
        return True

    def search_users(self, search_term: str, tenant_id: Optional[int] = None) -> List[User]:
        """البحث في المستخدمين"""
        query = self.db.query(User)
        
        if tenant_id:
            query = query.filter(User.tenant_id == tenant_id)
        
        # البحث في الاسم والإيميل واسم المستخدم
        search_condition = or_(
            User.first_name.contains(search_term),
            User.last_name.contains(search_term),
            User.email.contains(search_term),
            User.username.contains(search_term)
        )
        
        return query.filter(search_condition).all()

    def get_user_count_by_tenant(self, tenant_id: int) -> int:
        """عدد مستخدمي الشركة"""
        return self.db.query(User).filter(User.tenant_id == tenant_id).count()
