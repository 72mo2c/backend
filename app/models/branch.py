"""
نموذج الفروع (Branch) للنظام متعدد المستأجرين
يدعم إدارة فروع الشركات مع التحكم في الصلاحيات
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.models.associations import tenant_user


class Branch(BaseModel):
    """
    نموذج الفرع - يدعم فروع الشركة
    كل فرع يمكن أن يكون له صلاحيات منفصلة
    """
    __tablename__ = "branches"

    # المعرف الأساسي
    id = Column(Integer, primary_key=True, index=True)

    # ربط بالشركة
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    # معلومات الفرع الأساسية
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)  # رمز الفرع المميز
    description = Column(Text, nullable=True)

    # معلومات الاتصال
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    fax = Column(String(20), nullable=True)

    # العنوان والموقع
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True, index=True)

    # معلومات المحاسبة
    branch_tax_number = Column(String(50), nullable=True, unique=True, index=True)
    branch_registration_number = Column(String(50), nullable=True, unique=True)

    # معلومات الاتصال
    manager_name = Column(String(255), nullable=True)
    manager_email = Column(String(255), nullable=True, index=True)
    manager_phone = Column(String(20), nullable=True)

    # الإعدادات المحلية
    is_main_branch = Column(Boolean, default=False, index=True)  # فرع رئيسي أم لا
    currency = Column(String(10), nullable=False, default="SAR")  # عملة الفرع
    timezone = Column(String(50), nullable=True, default="Asia/Riyadh")
    language = Column(String(10), nullable=True, default="ar")
    
    # حالة الفرع
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)

    # معلومات النظام
    logo_url = Column(String(500), nullable=True)
    settings_json = Column(Text, nullable=True)  # JSON إعدادات مخصصة للفرع
    
    # التواريخ
    opened_at = Column(DateTime(timezone=True), nullable=True)  # تاريخ فتح الفرع
    closed_at = Column(DateTime(timezone=True), nullable=True)  # تاريخ إغلاق الفرع
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    # الشركة المرتبطة
    tenant = relationship("Tenant", back_populates="branches")
    
    # المستخدمون المرتبطون بالفرع
    users = relationship("User", secondary="branch_user", back_populates="branches")

    # دورات الفرع
    account_books = relationship("AccountBook", back_populates="branch", cascade="all, delete-orphan")

    # قيود الفريدة
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_branch_tenant_code'),
    )

    def __repr__(self) -> str:
        return f"<Branch(id={self.id}, name='{self.name}', tenant_id={self.tenant_id})>"

    @property
    def full_address(self) -> str:
        """تجميع العنوان الكامل للفرع"""
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
        """اسم عرض الفرع"""
        return f"{self.name} ({self.code})"

    def get_usage_stats(self) -> dict:
        """إحصائيات استخدام الفرع"""
        return {
            "current_users": len(self.users),
            "current_account_books": len(self.account_books),
            "is_active": self.is_active,
            "opened_date": self.opened_at.isoformat() if self.opened_at else None
        }