"""
API endpoints للشركات (Tenants) والنظام متعدد المستأجرين
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.branch import Branch
from app.schemas.tenant import (
    TenantResponse, TenantCreate, TenantUpdate, TenantWithStats, 
    TenantUserRoleCreate, TenantUserRoleResponse, TenantListResponse,
    TenantUsageStats
)
from app.schemas.branch import BranchResponse, BranchListResponse
from app.schemas.user import UserResponse
from app.api.deps import get_current_superuser, get_current_user
from app.services.tenant_service import TenantService
from app.services.branch_service import BranchService

router = APIRouter()

def get_tenant_service(db: Session = Depends(get_db)) -> TenantService:
    return TenantService(db)

def get_branch_service(db: Session = Depends(get_db)) -> BranchService:
    return BranchService(db)


@router.get("/", response_model=List[TenantResponse])
async def get_tenants(
    skip: int = Query(0, ge=0, description="عدد الأسطر لتخطيها"),
    limit: int = Query(100, ge=1, le=500, description="عدد الأسطر المراد جلبها"),
    search: Optional[str] = Query(None, description="البحث في الاسم أو الرمز أو البريد"),
    status: Optional[str] = Query(None, description="تصفية حسب الحالة (trial, active, suspended)"),
    plan_type: Optional[str] = Query(None, description="تصفية حسب نوع الخطة (basic, premium, enterprise)"),
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على قائمة الشركات مع التصفح والبحث"""
    return tenant_service.get_tenants(
        skip=skip, limit=limit, search=search, status=status, plan_type=plan_type
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على شركة محددة"""
    tenant = tenant_service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="الشركة غير موجودة")
    return tenant


@router.get("/{tenant_id}/stats", response_model=TenantWithStats)
async def get_tenant_stats(
    tenant_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على شركة مع الإحصائيات"""
    tenant_stats = tenant_service.get_tenant_with_stats(tenant_id)
    if not tenant_stats:
        raise HTTPException(status_code=404, detail="الشركة غير موجودة")
    return tenant_stats


@router.get("/{tenant_id}/usage-summary", response_model=dict)
async def get_tenant_usage_summary(
    tenant_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على ملخص استخدام الشركة"""
    try:
        return tenant_service.get_tenant_usage_summary(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{tenant_id}/branches", response_model=List[BranchResponse])
async def get_tenant_branches(
    tenant_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على فروع الشركة"""
    return branch_service.get_branches(tenant_id, skip=skip, limit=limit, search=search)


@router.get("/{tenant_id}/branches/summary", response_model=None)
async def get_tenant_branches_summary(
    tenant_id: int,
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على ملخص فروع الشركة"""
    try:
        return branch_service.get_tenant_branches_summary(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """إنشاء شركة جديدة"""
    try:
        return tenant_service.create_tenant(tenant_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """تحديث شركة"""
    try:
        return tenant_service.update_tenant(tenant_id, tenant_data)
    except ValueError as e:
        if "غير موجودة" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """حذف شركة"""
    try:
        tenant_service.delete_tenant(tenant_id)
        return {"message": "تم حذف الشركة بنجاح"}
    except ValueError as e:
        if "غير موجودة" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.post("/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """تفعيل شركة"""
    try:
        tenant_service.activate_tenant(tenant_id)
        return {"message": "تم تفعيل الشركة بنجاح"}
    except ValueError as e:
        if "غير موجودة" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.post("/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: int,
    reason: Optional[str] = Query(None, description="سبب الإيقاف"),
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """إيقاف شركة"""
    try:
        tenant_service.suspend_tenant(tenant_id, reason)
        return {"message": "تم إيقاف الشركة بنجاح"}
    except ValueError as e:
        if "غير موجودة" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.post("/{tenant_id}/users/{user_id}")
async def add_user_to_tenant(
    tenant_id: int,
    user_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """إضافة مستخدم للشركة"""
    try:
        tenant_service.add_user_to_tenant(tenant_id, user_id)
        return {"message": "تم إضافة المستخدم للشركة بنجاح"}
    except ValueError as e:
        if "غير موجودة" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.delete("/{tenant_id}/users/{user_id}")
async def remove_user_from_tenant(
    tenant_id: int,
    user_id: int,
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """إزالة مستخدم من الشركة"""
    try:
        tenant_service.remove_user_from_tenant(tenant_id, user_id)
        return {"message": "تم إزالة المستخدم من الشركة بنجاح"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.get("/{tenant_id}/users", response_model=List[UserResponse])
async def get_tenant_users(
    tenant_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على مستخدمي الشركة"""
    try:
        return tenant_service.get_tenant_users(tenant_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats/overview", response_model=None)
async def get_tenants_overview_stats(
    tenant_service: TenantService = Depends(get_tenant_service),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على إحصائيات عامة للشركات"""
    return {
        "total_tenants": tenant_service.count_total_tenants(),
        "active_tenants": tenant_service.count_active_tenants(),
        "timestamp": "2025-11-03T21:01:39Z"
    }
