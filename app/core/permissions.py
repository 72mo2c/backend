from typing import List, Set, Optional
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role_permission import Permission
from app.database import get_db


# صلاحيات النظام الأساسية
SYSTEM_PERMISSIONS = {
    # Users
    "users:create": "إنشاء مستخدمين",
    "users:read": "قراءة المستخدمين", 
    "users:update": "تحديث المستخدمين",
    "users:delete": "حذف المستخدمين",
    "users:manage": "إدارة المستخدمين",
    
    # Tenants
    "tenants:create": "إنشاء مستأجرين",
    "tenants:read": "قراءة المستأجرين",
    "tenants:update": "تحديث المستأجرين", 
    "tenants:delete": "حذف المستأجرين",
    "tenants:manage": "إدارة المستأجرين",
    
    # Roles & Permissions
    "roles:create": "إنشاء أدوار",
    "roles:read": "قراءة الأدوار",
    "roles:update": "تحديث الأدوار",
    "roles:delete": "حذف الأدوار",
    "permissions:manage": "إدارة الصلاحيات",
    
    # Subscriptions
    "subscriptions:create": "إنشاء اشتراكات",
    "subscriptions:read": "قراءة الاشتراكات",
    "subscriptions:update": "تحديث الاشتراكات",
    "subscriptions:delete": "إلغاء الاشتراكات",
    "subscriptions:manage": "إدارة الاشتراكات",
    
    # Branches
    "branches:create": "إنشاء فروع",
    "branches:read": "قراءة الفروع",
    "branches:update": "تحديث الفروع",
    "branches:delete": "حذف الفروع",
    "branches:manage": "إدارة الفروع",
    
    # System
    "system:admin": "إدارة النظام",
    "system:backup": "نسخ احتياطية",
    "system:logs": "عرض السجلات",
}


# أدوار النظام الأساسية
SYSTEM_ROLES = {
    "super_admin": {
        "description": "مدير النظام العام",
        "permissions": list(SYSTEM_PERMISSIONS.keys())
    },
    "tenant_admin": {
        "description": "مدير المستأجر",
        "permissions": [
            "users:create", "users:read", "users:update", "users:manage",
            "branches:create", "branches:read", "branches:update", "branches:manage",
            "tenants:read"
        ]
    },
    "branch_manager": {
        "description": "مدير الفرع",
        "permissions": [
            "users:create", "users:read", "users:update",
            "branches:read", "branches:update"
        ]
    },
    "employee": {
        "description": "موظف",
        "permissions": [
            "users:read",
            "branches:read"
        ]
    },
    "viewer": {
        "description": "مشاهد",
        "permissions": [
            "users:read",
            "branches:read"
        ]
    }
}


def check_permission(required_permission: str):
    """Decorator للتحقق من الصلاحية"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="يجب تسجيل الدخول أولاً"
                )
            
            # Superuser has all permissions
            if current_user.is_superuser:
                return await func(*args, **kwargs)
            
            # Check user's permissions
            user_permissions = set()
            for role in current_user.roles:
                for permission in role.permissions:
                    user_permissions.add(permission.name)
            
            # Check if user has required permission
            if required_permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"ليس لديك صلاحية {SYSTEM_PERMISSIONS.get(required_permission, required_permission)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions(user: User) -> Set[str]:
    """الحصول على صلاحيات المستخدم"""
    permissions = set()
    
    # Superuser has all permissions
    if user.is_superuser:
        return set(SYSTEM_PERMISSIONS.keys())
    
    # Get permissions from roles
    for role in user.roles:
        if role.is_active:
            for permission in role.permissions:
                permissions.add(permission.name)
    
    return permissions


def check_user_permission(user: User, required_permission: str) -> bool:
    """التحقق من صلاحية المستخدم"""
    if user.is_superuser:
        return True
    
    user_permissions = get_user_permissions(user)
    return required_permission in user_permissions


def has_any_permission(user: User, permissions: List[str]) -> bool:
    """التحقق من وجود أي من الصلاحيات المطلوبة"""
    if user.is_superuser:
        return True
    
    user_permissions = get_user_permissions(user)
    return any(perm in user_permissions for perm in permissions)


def has_all_permissions(user: User, permissions: List[str]) -> bool:
    """التحقق من وجود جميع الصلاحيات المطلوبة"""
    if user.is_superuser:
        return True
    
    user_permissions = get_user_permissions(user)
    return all(perm in user_permissions for perm in permissions)


def initialize_default_permissions(db: Session) -> List[Permission]:
    """إنشاء الصلاحيات الافتراضية للنظام"""
    permissions = []
    
    for perm_name, description in SYSTEM_PERMISSIONS.items():
        # Extract resource and action from permission name
        parts = perm_name.split(":")
        resource = parts[0] if len(parts) > 0 else ""
        action = parts[1] if len(parts) > 1 else ""
        
        # Check if permission already exists
        existing_perm = db.query(Permission).filter(Permission.name == perm_name).first()
        if not existing_perm:
            permission = Permission(
                name=perm_name,
                description=description,
                resource=resource,
                action=action
            )
            db.add(permission)
            permissions.append(permission)
    
    db.commit()
    return permissions
