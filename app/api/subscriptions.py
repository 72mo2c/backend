from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionResponse, SubscriptionCreate, SubscriptionUpdate, SubscriptionWithTenant
)
from app.api.deps import get_current_superuser
from app.services.subscription_service import SubscriptionService

router = APIRouter()
subscription_service = SubscriptionService()


@router.get("/", response_model=List[SubscriptionWithTenant])
async def get_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على قائمة الاشتراكات"""
    return subscription_service.get_subscriptions(
        db, skip=skip, limit=limit, status=status
    )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على اشتراك محدد"""
    return subscription_service.get_subscription(db, subscription_id=subscription_id)


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """إنشاء اشتراك جديد"""
    return subscription_service.create_subscription(db, subscription_data=subscription_data)


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """تحديث اشتراك"""
    return subscription_service.update_subscription(
        db, subscription_id=subscription_id, subscription_data=subscription_data
    )


@router.delete("/{subscription_id}")
async def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """إلغاء اشتراك"""
    subscription_service.cancel_subscription(db, subscription_id=subscription_id)
    return {"message": "تم إلغاء الاشتراك بنجاح"}


@router.get("/tenant/{tenant_id}", response_model=SubscriptionResponse)
async def get_tenant_subscription(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """الحصول على اشتراك مستأجر محدد"""
    return subscription_service.get_tenant_subscription(db, tenant_id=tenant_id)
