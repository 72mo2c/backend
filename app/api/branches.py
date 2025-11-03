"""
API endpoints للفروع والنظام متعدد المستأجرين
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.branch import Branch
from app.schemas.branch import (
    BranchResponse, BranchCreate, BranchUpdate, BranchWithStats,
    BranchUserCreate, BranchUserResponse, BranchListResponse
)
from app.schemas.user import UserResponse
from app.api.deps import get_current_active_user, get_current_superuser
from app.services.branch_service import BranchService

router = APIRouter()

def get_branch_service(db: Session = Depends(get_db)) -> BranchService:
    return BranchService(db)


@router.get("/", response_model=List[BranchResponse])
async def get_branches(
    tenant_id: int = Query(..., description="معرف الشركة"),
    skip: int = Query(0, ge=0, description="عدد الأسطر لتخطيها"),
    limit: int = Query(100, ge=1, le=500, description="عدد الأسطر المراد جلبها"),
    search: Optional[str] = Query(None, description="البحث في الاسم أو الرمز أو المدينة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على قائمة الفروع"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    return branch_service.get_branches(tenant_id, skip=skip, limit=limit, search=search)


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: int,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على فرع محدد"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    branch = branch_service.get_branch(branch_id, tenant_id)
    if not branch:
        raise HTTPException(status_code=404, detail="الفرع غير موجود")
    return branch


@router.get("/{branch_id}/stats", response_model=BranchWithStats)
async def get_branch_stats(
    branch_id: int,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على فرع مع الإحصائيات"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    branch_stats = branch_service.get_branch_with_stats(branch_id, tenant_id)
    if not branch_stats:
        raise HTTPException(status_code=404, detail="الفرع غير موجود")
    return branch_stats


@router.post("/", response_model=BranchResponse)
async def create_branch(
    branch_data: BranchCreate,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """إنشاء فرع جديد"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        return branch_service.create_branch(branch_data, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """تحديث فرع"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        return branch_service.update_branch(branch_id, branch_data, tenant_id)
    except ValueError as e:
        if "غير موجود" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.delete("/{branch_id}")
async def delete_branch(
    branch_id: int,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """حذف فرع"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        branch_service.delete_branch(branch_id, tenant_id)
        return {"message": "تم حذف الفرع بنجاح"}
    except ValueError as e:
        if "غير موجود" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.post("/{branch_id}/set-main")
async def set_main_branch(
    branch_id: int,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """تعيين فرع رئيسي"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        branch_service.set_main_branch(branch_id, tenant_id)
        return {"message": "تم تعيين الفرع كفرع رئيسي بنجاح"}
    except ValueError as e:
        if "غير موجود" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.post("/{branch_id}/users")
async def add_user_to_branch(
    branch_id: int,
    branch_data: BranchUserCreate,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """إضافة مستخدم للفرع"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        branch_service.add_user_to_branch(branch_id, branch_data.user_id, branch_data.is_primary)
        return {"message": "تم إضافة المستخدم للفرع بنجاح"}
    except ValueError as e:
        if "غير موجود" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.delete("/{branch_id}/users/{user_id}")
async def remove_user_from_branch(
    branch_id: int,
    user_id: int,
    tenant_id: int = Query(..., description="معرف الشركة"),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """إزالة مستخدم من الفرع"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        branch_service.remove_user_from_branch(branch_id, user_id)
        return {"message": "تم إزالة المستخدم من الفرع بنجاح"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الخادم: {str(e)}")


@router.get("/{branch_id}/users", response_model=List[UserResponse])
async def get_branch_users(
    branch_id: int,
    tenant_id: int = Query(..., description="معرف الشركة"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على مستخدمي الفرع"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    try:
        return branch_service.get_branch_users(branch_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{tenant_id}/main-branch", response_model=BranchResponse)
async def get_main_branch(
    tenant_id: int,
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على الفرع الرئيسي للشركة"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    main_branch = branch_service.get_main_branch(tenant_id)
    if not main_branch:
        raise HTTPException(status_code=404, detail="لا يوجد فرع رئيسي لهذه الشركة")
    return main_branch


@router.get("/{tenant_id}/branches/count", response_model=None)
async def get_tenant_branches_count(
    tenant_id: int,
    branch_service: BranchService = Depends(get_branch_service),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على عدد فروع الشركة"""
    # التحقق من صلاحية الوصول للشركة
    if not current_user.is_member_of_company(tenant_id):
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية للوصول إلى هذه الشركة")
    
    return {
        "tenant_id": tenant_id,
        "total_branches": branch_service.get_branches_count(tenant_id),
        "active_branches": branch_service.get_active_branches_count(tenant_id)
    }
