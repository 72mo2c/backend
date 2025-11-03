from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from app.models.subscription import Subscription, SubscriptionStatus, BillingCycle
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class SubscriptionService:
    """خدمة إدارة الاشتراكات"""
    
    def get_subscriptions(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[Subscription]:
        """الحصول على قائمة الاشتراكات"""
        query = db.query(Subscription)
        
        if status:
            query = query.filter(Subscription.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_subscription(self, db: Session, subscription_id: int) -> Optional[Subscription]:
        """الحصول على اشتراك محدد"""
        return db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    def create_subscription(self, db: Session, subscription_data: SubscriptionCreate) -> Subscription:
        """إنشاء اشتراك جديد"""
        # Calculate dates based on billing cycle
        now = datetime.utcnow()
        if subscription_data.billing_cycle == BillingCycle.MONTHLY:
            period_end = now + timedelta(days=30)
        else:  # YEARLY
            period_end = now + timedelta(days=365)
        
        db_subscription = Subscription(
            tenant_id=subscription_data.tenant_id,
            plan_name=subscription_data.plan_name,
            billing_cycle=subscription_data.billing_cycle,
            amount=0.00,  # Set default amount
            current_period_start=now,
            current_period_end=period_end,
            status=SubscriptionStatus.TRIALING
        )
        
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        return db_subscription
    
    def update_subscription(
        self, 
        db: Session, 
        subscription_id: int, 
        subscription_data: SubscriptionUpdate
    ) -> Optional[Subscription]:
        """تحديث اشتراك"""
        db_subscription = self.get_subscription(db, subscription_id)
        if not db_subscription:
            return None
        
        update_data = subscription_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_subscription, field, value)
        
        db.commit()
        db.refresh(db_subscription)
        return db_subscription
    
    def cancel_subscription(self, db: Session, subscription_id: int) -> bool:
        """إلغاء اشتراك"""
        db_subscription = self.get_subscription(db, subscription_id)
        if not db_subscription:
            return False
        
        db_subscription.status = SubscriptionStatus.CANCELED
        db_subscription.canceled_at = datetime.utcnow()
        db.commit()
        return True
    
    def get_tenant_subscription(self, db: Session, tenant_id: int) -> Optional[Subscription]:
        """الحصول على اشتراك مستأجر محدد"""
        return db.query(Subscription).filter(
            and_(
                Subscription.tenant_id == tenant_id,
                Subscription.status != SubscriptionStatus.CANCELED
            )
        ).first()
    
    def check_subscription_expiry(self, db: Session):
        """فحص انتهاء الاشتراكات"""
        now = datetime.utcnow()
        expired_subscriptions = db.query(Subscription).filter(
            and_(
                Subscription.current_period_end < now,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        ).all()
        
        for subscription in expired_subscriptions:
            subscription.status = SubscriptionStatus.EXPIRED
            db.commit()
        
        return len(expired_subscriptions)
