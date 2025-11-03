"""
مخططات البيانات (Schemas) للشركات والنظام متعدد المستأجرين
تستخدم Pydantic للتحقق من البيانات
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from pydantic import root_validator


class TenantBase(BaseModel):
    """المخطط الأساسي للشركة"""
    name: str = Field(..., min_length=2, max_length=255, description="اسم الشركة")
    code: str = Field(..., min_length=2, max_length=50, description="رمز الشركة المميز")
    email: Optional[EmailStr] = Field(None, description="البريد الإلكتروني للشركة")
    phone: Optional[str] = Field(None, max_length=20, description="رقم الهاتف")
    website: Optional[str] = Field(None, description="الموقع الإلكتروني")
    
    # العنوان
    address_line1: Optional[str] = Field(None, max_length=255, description="العنوان الأول")
    address_line2: Optional[str] = Field(None, max_length=255, description="العنوان الثاني")
    city: Optional[str] = Field(None, max_length=100, description="المدينة")
    state: Optional[str] = Field(None, max_length=100, description="الولاية/المحافظة")
    postal_code: Optional[str] = Field(None, max_length=20, description="الرمز البريدي")
    country: Optional[str] = Field(None, max_length=100, description="البلد")
    
    # معلومات الضريبة
    tax_number: Optional[str] = Field(None, max_length=50, description="رقم الضريبة")
    registration_number: Optional[str] = Field(None, max_length=50, description="رقم التسجيل")
    
    # معلومات الاتصال
    contact_person_name: Optional[str] = Field(None, max_length=255, description="اسم الشخص المسؤول")
    contact_person_email: Optional[EmailStr] = Field(None, description="بريد الشخص المسؤول")
    contact_person_phone: Optional[str] = Field(None, max_length=20, description="هاتف الشخص المسؤول")
    
    # إعدادات الخطة
    plan_type: Optional[str] = Field("basic", description="نوع الخطة: basic, premium, enterprise")
    max_users: Optional[int] = Field(5, ge=1, description="الحد الأقصى للمستخدمين")
    max_branches: Optional[int] = Field(1, ge=1, description="الحد الأقصى للفروع")
    max_storage_gb: Optional[int] = Field(1, ge=1, description="الحد الأقصى للتخزين (جيجابايت)")
    
    # حالة الاشتراك
    subscription_status: Optional[str] = Field("trial", description="حالة الاشتراك")
    trial_ends_at: Optional[datetime] = Field(None, description="نهاية الفترة التجريبية")
    subscription_ends_at: Optional[datetime] = Field(None, description="نهاية الاشتراك")
    
    # معلومات النظام
    logo_url: Optional[HttpUrl] = Field(None, description="رابط شعار الشركة")
    is_active: Optional[bool] = Field(True, description="حالة النشاط")
    is_verified: Optional[bool] = Field(False, description="حالة التحقق")


class TenantCreate(TenantBase):
    """مخطط إنشاء شركة جديدة"""
    
    @validator('code')
    def validate_code(cls, v):
        """التحقق من صحة رمز الشركة"""
        import re
        if not re.match(r'^[A-Z0-9_]+$', v):
            raise ValueError('رمز الشركة يجب أن يحتوي على أحرف كبيرة وأرقام وخط سفلي فقط')
        return v.upper()
    
    @validator('name')
    def validate_name(cls, v):
        """التحقق من صحة اسم الشركة"""
        if len(v.strip()) < 2:
            raise ValueError('اسم الشركة يجب أن يكون على الأقل حرفين')
        return v.strip()


class TenantUpdate(BaseModel):
    """مخطط تحديث الشركة"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[HttpUrl] = None
    
    # العنوان
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # معلومات الضريبة
    tax_number: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)
    
    # معلومات الاتصال
    contact_person_name: Optional[str] = Field(None, max_length=255)
    contact_person_email: Optional[EmailStr] = None
    contact_person_phone: Optional[str] = Field(None, max_length=20)
    
    # إعدادات الخطة
    plan_type: Optional[str] = Field(None, description="basic, premium, enterprise")
    max_users: Optional[int] = Field(None, ge=1)
    max_branches: Optional[int] = Field(None, ge=1)
    max_storage_gb: Optional[int] = Field(None, ge=1)
    
    # حالة الاشتراك
    subscription_status: Optional[str] = None
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    
    # معلومات النظام
    logo_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class TenantResponse(TenantBase):
    """مخطط استجابة الشركة"""
    id: int
    full_address: Optional[str] = None
    is_trial_active: bool = False
    trial_days_remaining: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TenantUsageStats(BaseModel):
    """إحصائيات استخدام الشركة"""
    current_users: int
    current_branches: int
    storage_used_gb: float
    is_trial_active: bool
    trial_days_remaining: int
    users_percentage: float = 0.0
    branches_percentage: float = 0.0


class TenantWithStats(TenantResponse):
    """الشركة مع الإحصائيات"""
    usage_stats: TenantUsageStats


class TenantUserRoleBase(BaseModel):
    """مخطط أساسي لدور المستخدم في الشركة"""
    user_id: int = Field(..., description="معرف المستخدم")
    role_id: int = Field(..., description="معرف الدور")
    branch_id: Optional[int] = Field(None, description="معرف الفرع")
    is_active: Optional[bool] = Field(True, description="حالة النشاط")


class TenantUserRoleCreate(TenantUserRoleBase):
    """إنشاء دور مستخدم في شركة"""
    granted_by: Optional[int] = Field(None, description="معرف المستخدم الذي منح الدور")


class TenantUserRoleResponse(TenantUserRoleBase):
    """استجابة دور المستخدم في الشركة"""
    id: int
    tenant_id: int
    granted_by: Optional[int]
    granted_at: datetime
    
    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """قائمة الشركات مع التصفح"""
    items: List[TenantResponse]
    total: int
    page: int
    size: int
    pages: int
