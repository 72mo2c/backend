from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserList
from app.api.deps import get_current_active_user, get_current_superuser
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على قائمة المستخدمين"""
    user_service = UserService(db)
    return user_service.get_users(db, skip=skip, limit=limit, search=search)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """الحصول على معلومات المستخدم الحالي"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """الحصول على مستخدم محدد"""
    return user_service.get_user(db, user_id=user_id)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """إنشاء مستخدم جديد"""
    return user_service.create_user(db, user_data=user_data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """تحديث مستخدم"""
    return user_service.update_user(db, user_id=user_id, user_data=user_data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """حذف مستخدم"""
    user_service.delete_user(db, user_id=user_id)
    return {"message": "تم حذف المستخدم بنجاح"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """تفعيل مستخدم"""
    user_service.activate_user(db, user_id=user_id)
    return {"message": "تم تفعيل المستخدم بنجاح"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """إلغاء تفعيل مستخدم"""
    user_service.deactivate_user(db, user_id=user_id)
    return {"message": "تم إلغاء تفعيل المستخدم بنجاح"}
