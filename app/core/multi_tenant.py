from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import decode_access_token


class TenantContext:
    """سياق المستأجر الحالي"""
    
    def __init__(self):
        self.current_tenant: Optional[Tenant] = None
        self.current_user: Optional[User] = None
    
    def set_from_token(self, token_data: Dict[str, Any]):
        """تعيين السياق من بيانات الرمز"""
        if "tenant_id" in token_data:
            self.tenant_id = token_data["tenant_id"]
        if "sub" in token_data:
            self.user_id = token_data["sub"]
    
    def get_tenant_from_db(self, db: Session) -> Optional[Tenant]:
        """الحصول على المستأجر من قاعدة البيانات"""
        if hasattr(self, 'tenant_id') and self.tenant_id:
            self.current_tenant = db.query(Tenant).filter(
                Tenant.id == self.tenant_id
            ).first()
        return self.current_tenant
    
    def get_user_from_db(self, db: Session) -> Optional[User]:
        """الحصول على المستخدم من قاعدة البيانات"""
        if hasattr(self, 'user_id') and self.user_id:
            self.current_user = db.query(User).filter(
                User.id == self.user_id
            ).first()
        return self.current_user


def get_current_tenant_context(
    request: Request,
    db: Session
) -> TenantContext:
    """الحصول على سياق المستأجر الحالي من الطلب"""
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز المصادقة مطلوب"
        )
    
    token = auth_header.split(" ")[1]
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز غير صالح"
        )
    
    # Create tenant context
    context = TenantContext()
    context.set_from_token(payload)
    
    # Verify tenant exists and is active
    tenant = context.get_tenant_from_db(db)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="المستأجر غير موجود"
        )
    
    if tenant.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="المستأجر غير نشط"
        )
    
    return context


def get_current_user_context(
    request: Request,
    db: Session
) -> TenantContext:
    """الحصول على سياق المستخدم الحالي من الطلب"""
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز المصادقة مطلوب"
        )
    
    token = auth_header.split(" ")[1]
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز غير صالح"
        )
    
    # Create tenant context
    context = TenantContext()
    context.set_from_token(payload)
    
    # Verify user exists and is active
    user = context.get_user_from_db(db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="المستخدم غير موجود"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="حساب المستخدم معطل"
        )
    
    return context


def ensure_user_in_tenant(
    user: User, 
    tenant_id: int,
    raise_exception: bool = True
) -> bool:
    """التأكد من أن المستخدم ينتمي للمستأجر المحدد"""
    if user.tenant_id == tenant_id:
        return True
    
    if raise_exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غير مسموح بالوصول إلى موارد هذا المستأجر"
        )
    
    return False


def check_tenant_subscription_limits(
    tenant: Tenant,
    resource_type: str,
    current_count: int
) -> bool:
    """فحص حدود الاشتراك للمستأجر"""
    limits = {
        "users": tenant.max_users,
        "branches": tenant.max_branches
    }
    
    if resource_type in limits:
        return current_count < limits[resource_type]
    
    return True


def get_tenant_stats(db: Session, tenant_id: int) -> Dict[str, int]:
    """الحصول على إحصائيات المستأجر"""
    from app.models.user import User
    from app.models.organizational import Branch
    
    user_count = db.query(User).filter(User.tenant_id == tenant_id).count()
    branch_count = db.query(Branch).filter(Branch.tenant_id == tenant_id).count()
    
    return {
        "users": user_count,
        "branches": branch_count,
        "max_users": None,  # Will be loaded from tenant
        "max_branches": None  # Will be loaded from tenant
    }
