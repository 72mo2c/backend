"""
نموذج الشركة (Tenant) للنظام متعدد المستأجرين
يدعم إدارة الشركات والفروع مع التحكم في الصلاحيات
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.models.associations import tenant_user


class Tenant(BaseModel):
    """
    نموذج الشركة - يدعم النظام متعدد المستأجرين
    كل شركة لها معرف فريد وقاعدة بيانات معزولة
    """
    __tablename__ = "tenants"

    # المعرف الأساسي
    id = Column(Integer, primary_key=True, index=True)

    # معلومات الشركة الأساسية
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)  # رمز الشركة المميز
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)

    # العنوان والموقع
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True, index=True)

    # معلومات الضريبة والتسجيل
    tax_number = Column(String(50), nullable=True, unique=True, index=True)
    registration_number = Column(String(50), nullable=True, unique=True)
    
    # معلومات الاتصال
    contact_person_name = Column(String(255), nullable=True)
    contact_person_email = Column(String(255), nullable=True, index=True)
    contact_person_phone = Column(String(20), nullable=True)

    # إعدادات الخطة والاشتراك
    plan_type = Column(String(50), nullable=False, default="basic")  # basic, premium, enterprise
    max_users = Column(Integer, nullable=False, default=5)
    max_branches = Column(Integer, nullable=False, default=1)
    max_storage_gb = Column(Integer, nullable=False, default=1)  # جيجابايت
    
    # حالة الاشتراك
    subscription_status = Column(String(20), nullable=False, default="trial")  # active, suspended, cancelled, trial
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # حالة الشركة
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    
    # معلومات النظام
    logo_url = Column(String(500), nullable=True)
    settings_json = Column(Text, nullable=True)  # JSON إعدادات مخصصة
    
    # التواريخ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    # المستخدمون المرتبطون بالشركة
    users = relationship("User", secondary="tenant_user", back_populates="tenants")
    
    # الفروع المرتبطة بالشركة
    branches = relationship("Branch", back_populates="tenant", cascade="all, delete-orphan")

    # الصفحات المرتبطة بالشركة
    pages = relationship("Page", back_populates="tenant", cascade="all, delete-orphan")

    # دورات الشركة
    account_books = relationship("AccountBook", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, name='{self.name}', code='{self.code}')>"

    @property
    def full_address(self) -> str:
        """تجميع العنوان الكامل"""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    @property
    def display_name(self) -> str:
        """اسم العرض للشركة"""
        return self.name or self.code

    def is_trial_active(self) -> bool:
        """فحص ما إذا كانت الفترة التجريبية نشطة"""
        if self.trial_ends_at and self.subscription_status == "trial":
            from datetime import datetime, timezone
            return self.trial_ends_at > datetime.now(timezone.utc)
        return False

    def get_usage_stats(self) -> dict:
        """إحصائيات استخدام الشركة"""
        return {
            "current_users": len(self.users),
            "current_branches": len(self.branches),
            "storage_used_gb": 0,  # سيتم حسابها لاحقاً
            "is_trial_active": self.is_trial_active(),
            "trial_days_remaining": self.get_trial_days_remaining()
        }

    def get_trial_days_remaining(self) -> int:
        """أيام متبقية في الفترة التجريبية"""
        if not self.is_trial_active():
            return 0
        
        from datetime import datetime, timezone, timedelta
        remaining = self.trial_ends_at - datetime.now(timezone.utc)
        return max(0, remaining.days)


class TenantUserRole(BaseModel):
    """جدول الربط بين الشركة والمستخدم والدور"""
    __tablename__ = "tenant_user_roles"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    role_id = Column(Integer, nullable=False, index=True)
    branch_id = Column(Integer, nullable=True, index=True)  # اختياري - ربط بد فرع معين
    
    # معلومات إضافية
    is_active = Column(Boolean, default=True, index=True)
    granted_by = Column(Integer, nullable=True)  # المستخدم الذي منح هذا الدور
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # القيود الفريدة
    __table_args__ = (
        UniqueConstraint('tenant_id', 'user_id', 'branch_id', name='uq_tenant_user_branch_role'),
    )
