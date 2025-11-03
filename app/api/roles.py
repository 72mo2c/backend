from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.schemas.role_permission import (
    RoleResponse, RoleCreate, RoleUpdate, RoleList,
    PermissionResponse, PermissionCreate,
    UserRoleAssignment
)
from app.api.deps import get_current_superuser
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


# Roles endpoints
@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على قائمة الأدوار"""
    auth_service = AuthService(db)
    return auth_service.get_roles(skip=skip, limit=limit)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على دور محدد"""
    auth_service = AuthService(db)
    return auth_service.get_role(role_id=role_id)


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """إنشاء دور جديد"""
    auth_service = AuthService(db)
    return auth_service.create_role(role_data=role_data)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """تحديث دور"""
    auth_service = AuthService(db)
    return auth_service.update_role(role_id=role_id, role_data=role_data)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """حذف دور"""
    auth_service = AuthService(db)
    auth_service.delete_role(role_id=role_id)
    return {"message": "تم حذف الدور بنجاح"}


# Permissions endpoints
@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على قائمة الصلاحيات"""
    auth_service = AuthService(db)
    return auth_service.get_permissions()


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """إنشاء صلاحية جديدة"""
    auth_service = AuthService(db)
    return auth_service.create_permission(permission_data=permission_data)


# User-Role assignments
@router.post("/users/{user_id}/roles")
async def assign_roles_to_user(
    user_id: int,
    role_assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """تعيين أدوار لمستخدم"""
    auth_service = AuthService(db)
    auth_service.assign_roles_to_user(user_id=user_id, role_ids=role_assignment.role_ids)
    return {"message": "تم تعيين الأدوار للمستخدم بنجاح"}


@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على أدوار المستخدم"""
    auth_service = AuthService(db)
    return auth_service.get_user_roles(user_id=user_id)
