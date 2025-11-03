from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal as DecimalType
import enum

from app.models.base import BaseModel


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class BillingCycle(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Subscription(BaseModel):
    __tablename__ = "subscriptions"
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    plan_name = Column(String(50), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIALING)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    
    # Pricing
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Dates
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Stripe integration (للتطوير المستقبلي)
    stripe_subscription_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="subscription")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, tenant_id={self.tenant_id}, plan={self.plan_name})>"
