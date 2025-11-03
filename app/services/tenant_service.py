"""
خدمة إدارة الشركات (TenantService) للنظام متعدد المستأجرين
تدير عمليات CRUD للشركات والفروع مع التحكم في الصلاحيات
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from app.models.tenant import Tenant, TenantUserRole
from app.models.branch import Branch
from app.models.user import User
from app.models.associations import tenant_user
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantWithStats, TenantUsageStats


class TenantService:
    """خدمة إدارة الشركات"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_tenants(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        status: Optional[str] = None,
        plan_type: Optional[str] = None
    ) -> List[Tenant]:
        """الحصول على قائمة الشركات"""
        query = self.db.query(Tenant)
        
        # البحث
        if search:
            query = query.filter(
                or_(
                    Tenant.name.contains(search),
                    Tenant.code.contains(search),
                    Tenant.email.contains(search),
                    Tenant.city.contains(search),
                    Tenant.country.contains(search)
                )
            )
        
        # التصفية بالحالة
        if status:
            query = query.filter(Tenant.subscription_status == status)
        
        # التصفية بنوع الخطة
        if plan_type:
            query = query.filter(Tenant.plan_type == plan_type)
        
        return query.offset(skip).limit(limit).all()
    
    def get_tenant(self, tenant_id: int) -> Optional[Tenant]:
        """الحصول على شركة بالمعرف"""
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    def get_tenant_by_code(self, code: str) -> Optional[Tenant]:
        """الحصول على شركة بالرمز"""
        return self.db.query(Tenant).filter(Tenant.code == code).first()
    
    def get_tenant_by_email(self, email: str) -> Optional[Tenant]:
        """الحصول على شركة بالبريد الإلكتروني"""
        return self.db.query(Tenant).filter(Tenant.email == email).first()
    
    def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """إنشاء شركة جديدة"""
        try:
            # التحقق من وجود الرمز
            if self.get_tenant_by_code(tenant_data.code):
                raise ValueError(f"رمز الشركة '{tenant_data.code}' موجود بالفعل")
            
            # التحقق من وجود البريد الإلكتروني
            if tenant_data.email and self.get_tenant_by_email(tenant_data.email):
                raise ValueError(f"البريد الإلكتروني '{tenant_data.email}' مستخدم بالفعل")
            
            # إنشاء الشركة
            tenant = Tenant(
                name=tenant_data.name,
                code=tenant_data.code,
                email=tenant_data.email,
                phone=tenant_data.phone,
                website=tenant_data.website,
                address_line1=tenant_data.address_line1,
                address_line2=tenant_data.address_line2,
                city=tenant_data.city,
                state=tenant_data.state,
                postal_code=tenant_data.postal_code,
                country=tenant_data.country,
                tax_number=tenant_data.tax_number,
                registration_number=tenant_data.registration_number,
                contact_person_name=tenant_data.contact_person_name,
                contact_person_email=tenant_data.contact_person_email,
                contact_person_phone=tenant_data.contact_person_phone,
                plan_type=tenant_data.plan_type,
                max_users=tenant_data.max_users,
                max_branches=tenant_data.max_branches,
                max_storage_gb=tenant_data.max_storage_gb,
                subscription_status=tenant_data.subscription_status,
                trial_ends_at=tenant_data.trial_ends_at,
                subscription_ends_at=tenant_data.subscription_ends_at,
                logo_url=tenant_data.logo_url,
                is_active=tenant_data.is_active,
                is_verified=tenant_data.is_verified
            )
            
            # إضافة الفترة التجريبية إذا لم تكن محددة
            if not tenant.trial_ends_at:
                tenant.trial_ends_at = datetime.utcnow() + timedelta(days=30)
            
            self.db.add(tenant)
            self.db.commit()
            self.db.refresh(tenant)
            
            return tenant
            
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower():
                if "tenants_code_key" in str(e):
                    raise ValueError(f"رمز الشركة '{tenant_data.code}' موجود بالفعل")
                elif "tenants_email_key" in str(e):
                    raise ValueError(f"البريد الإلكتروني '{tenant_data.email}' مستخدم بالفعل")
            raise ValueError("خطأ في إنشاء الشركة")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في إنشاء الشركة: {str(e)}")
    
    def update_tenant(self, tenant_id: int, tenant_data: TenantUpdate) -> Optional[Tenant]:
        """تحديث شركة"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        try:
            # تحديث البيانات
            update_data = tenant_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(tenant, field):
                    setattr(tenant, field, value)
            
            tenant.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(tenant)
            
            return tenant
            
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower():
                if "tenants_code_key" in str(e):
                    raise ValueError(f"رمز الشركة '{tenant_data.code}' موجود بالفعل")
                elif "tenants_email_key" in str(e):
                    raise ValueError(f"البريد الإلكتروني '{tenant_data.email}' مستخدم بالفعل")
            raise ValueError("خطأ في تحديث الشركة")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في تحديث الشركة: {str(e)}")
    
    def delete_tenant(self, tenant_id: int) -> bool:
        """حذف شركة"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        try:
            self.db.delete(tenant)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في حذف الشركة: {str(e)}")
    
    def get_tenant_with_stats(self, tenant_id: int) -> Optional[TenantWithStats]:
        """الحصول على شركة مع الإحصائيات"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None
        
        # حساب الإحصائيات
        current_users = len(tenant.users)
        current_branches = len(tenant.branches)
        storage_used_gb = 0.0  # سيتم حسابها لاحقاً
        
        usage_stats = TenantUsageStats(
            current_users=current_users,
            current_branches=current_branches,
            storage_used_gb=storage_used_gb,
            is_trial_active=tenant.is_trial_active(),
            trial_days_remaining=tenant.get_trial_days_remaining()
        )
        
        # حساب النسب المئوية
        if tenant.max_users > 0:
            usage_stats.users_percentage = (current_users / tenant.max_users) * 100
        if tenant.max_branches > 0:
            usage_stats.branches_percentage = (current_branches / tenant.max_branches) * 100
        
        tenant_response = TenantResponse.from_orm(tenant)
        return TenantWithStats(tenant_response, usage_stats)
    
    def add_user_to_tenant(self, tenant_id: int, user_id: int) -> bool:
        """إضافة مستخدم للشركة"""
        # التحقق من وجود الشركة
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        # التحقق من وجود المستخدم
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"المستخدم بالمعرف {user_id} غير موجود")
        
        # التحقق من عدم وجود الربط مسبقاً
        existing = self.db.query(tenant_user).filter(
            and_(
                tenant_user.c.tenant_id == tenant_id,
                tenant_user.c.user_id == user_id
            )
        ).first()
        
        if existing:
            raise ValueError("المستخدم مرتبط بالشركة مسبقاً")
        
        try:
            # إضافة الربط
            self.db.execute(
                tenant_user.insert().values(tenant_id=tenant_id, user_id=user_id)
            )
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في إضافة المستخدم للشركة: {str(e)}")
    
    def remove_user_from_tenant(self, tenant_id: int, user_id: int) -> bool:
        """إزالة مستخدم من الشركة"""
        try:
            result = self.db.execute(
                tenant_user.delete().where(
                    and_(
                        tenant_user.c.tenant_id == tenant_id,
                        tenant_user.c.user_id == user_id
                    )
                )
            )
            self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في إزالة المستخدم من الشركة: {str(e)}")
    
    def get_tenant_users(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """الحصول على مستخدمي الشركة"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        return tenant.users[skip:skip + limit]
    
    def activate_tenant(self, tenant_id: int) -> bool:
        """تفعيل شركة"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        tenant.is_active = True
        tenant.subscription_status = "active"
        tenant.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def suspend_tenant(self, tenant_id: int, reason: str = None) -> bool:
        """إيقاف شركة"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        tenant.is_active = False
        tenant.subscription_status = "suspended"
        tenant.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def count_active_tenants(self) -> int:
        """عدد الشركات النشطة"""
        return self.db.query(Tenant).filter(Tenant.is_active == True).count()
    
    def count_total_tenants(self) -> int:
        """عدد الشركات الإجمالي"""
        return self.db.query(Tenant).count()
    
    def get_tenant_usage_summary(self, tenant_id: int) -> Dict[str, Any]:
        """ملخص استخدام الشركة"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "plan_type": tenant.plan_type,
            "subscription_status": tenant.subscription_status,
            "users": {
                "current": len(tenant.users),
                "max": tenant.max_users,
                "percentage": (len(tenant.users) / tenant.max_users * 100) if tenant.max_users > 0 else 0
            },
            "branches": {
                "current": len(tenant.branches),
                "max": tenant.max_branches,
                "percentage": (len(tenant.branches) / tenant.max_branches * 100) if tenant.max_branches > 0 else 0
            },
            "trial": {
                "is_active": tenant.is_trial_active(),
                "days_remaining": tenant.get_trial_days_remaining(),
                "ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None
            }
        }
