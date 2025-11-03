from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SubscriptionBase(BaseModel):
    plan_name: str
    billing_cycle: str  # monthly, yearly


class SubscriptionCreate(SubscriptionBase):
    tenant_id: int


class SubscriptionResponse(SubscriptionBase):
    id: int
    tenant_id: int
    status: str
    amount: Decimal
    currency: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    plan_name: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[Decimal] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None


class SubscriptionWithTenant(SubscriptionResponse):
    tenant_name: str
    tenant_slug: str
