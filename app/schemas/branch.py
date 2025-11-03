"""
مخططات البيانات (Schemas) للفروع والنظام متعدد المستأجرين
تستخدم Pydantic للتحقق من البيانات
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from pydantic import root_validator


class BranchBase(BaseModel):
    """المخطط الأساسي للفرع"""
    name: str = Field(..., min_length=2, max_length=255, description="اسم الفرع")
    code: str = Field(..., min_length=2, max_length=50, description="رمز الفرع المميز")
    description: Optional[str] = Field(None, description="وصف الفرع")
    
    # معلومات الاتصال
    email: Optional[EmailStr] = Field(None, description="البريد الإلكتروني للفرع")
    phone: Optional[str] = Field(None, max_length=20, description="رقم الهاتف")
    fax: Optional[str] = Field(None, max_length=20, description="رقم الفاكس")
    
    # العنوان
    address_line1: Optional[str] = Field(None, max_length=255, description="العنوان الأول")
    address_line2: Optional[str] = Field(None, max_length=255, description="العنوان الثاني")
    city: Optional[str] = Field(None, max_length=100, description="المدينة")
    state: Optional[str] = Field(None, max_length=100, description="الولاية/المحافظة")
    postal_code: Optional[str] = Field(None, max_length=20, description="الرمز البريدي")
    country: Optional[str] = Field(None, max_length=100, description="البلد")
    
    # معلومات المحاسبة
    branch_tax_number: Optional[str] = Field(None, max_length=50, description="رقم الضريبة للفرع")
    branch_registration_number: Optional[str] = Field(None, max_length=50, description="رقم التسجيل للفرع")
    
    # معلومات المدير
    manager_name: Optional[str] = Field(None, max_length=255, description="اسم مدير الفرع")
    manager_email: Optional[EmailStr] = Field(None, description="بريد مدير الفرع")
    manager_phone: Optional[str] = Field(None, max_length=20, description="هاتف مدير الفرع")
    
    # إعدادات محلية
    is_main_branch: Optional[bool] = Field(False, description="هل هو الفرع الرئيسي")
    currency: Optional[str] = Field("SAR", max_length=10, description="عملة الفرع")
    timezone: Optional[str] = Field("Asia/Riyadh", max_length=50, description="المنطقة الزمنية")
    language: Optional[str] = Field("ar", max_length=10, description="لغة الفرع")
    
    # معلومات النظام
    logo_url: Optional[HttpUrl] = Field(None, description="رابط شعار الفرع")
    is_active: Optional[bool] = Field(True, description="حالة النشاط")
    is_verified: Optional[bool] = Field(False, description="حالة التحقق")
    
    # تواريخ
    opened_at: Optional[datetime] = Field(None, description="تاريخ فتح الفرع")


class BranchCreate(BranchBase):
    """مخطط إنشاء فرع جديد"""
    
    @validator('code')
    def validate_code(cls, v):
        """التحقق من صحة رمز الفرع"""
        import re
        if not re.match(r'^[A-Z0-9_]+$', v):
            raise ValueError('رمز الفرع يجب أن يحتوي على أحرف كبيرة وأرقام وخط سفلي فقط')
        return v.upper()
    
    @validator('name')
    def validate_name(cls, v):
        """التحقق من صحة اسم الفرع"""
        if len(v.strip()) < 2:
            raise ValueError('اسم الفرع يجب أن يكون على الأقل حرفين')
        return v.strip()
    
    @validator('currency')
    def validate_currency(cls, v):
        """التحقق من صحة العملة"""
        valid_currencies = ['SAR', 'AED', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD', 'EGP', 'USD', 'EUR']
        if v not in valid_currencies:
            raise ValueError(f'العملة غير مدعومة. العملات المدعومة: {", ".join(valid_currencies)}')
        return v.upper()


class BranchUpdate(BaseModel):
    """مخطط تحديث الفرع"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    
    # معلومات الاتصال
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    fax: Optional[str] = Field(None, max_length=20)
    
    # العنوان
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # معلومات المحاسبة
    branch_tax_number: Optional[str] = Field(None, max_length=50)
    branch_registration_number: Optional[str] = Field(None, max_length=50)
    
    # معلومات المدير
    manager_name: Optional[str] = Field(None, max_length=255)
    manager_email: Optional[EmailStr] = None
    manager_phone: Optional[str] = Field(None, max_length=20)
    
    # إعدادات محلية
    is_main_branch: Optional[bool] = None
    currency: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    
    # معلومات النظام
    logo_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    
    # تواريخ
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = Field(None, description="تاريخ إغلاق الفرع")


class BranchResponse(BranchBase):
    """مخطط استجابة الفرع"""
    id: int
    tenant_id: int
    full_address: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BranchUsageStats(BaseModel):
    """إحصائيات استخدام الفرع"""
    current_users: int
    current_account_books: int
    is_active: bool
    opened_date: Optional[str] = None


class BranchWithStats(BranchResponse):
    """الفرع مع الإحصائيات"""
    usage_stats: BranchUsageStats


class BranchUserBase(BaseModel):
    """مخطط أساسي لربط المستخدم بالفرع"""
    user_id: int = Field(..., description="معرف المستخدم")
    branch_id: int = Field(..., description="معرف الفرع")
    is_active: Optional[bool] = Field(True, description="حالة النشاط")
    is_primary: Optional[bool] = Field(False, description="هل هو الفرع الأساسي للمستخدم")


class BranchUserCreate(BranchUserBase):
    """إنشاء ربط مستخدم بفرع"""
    pass


class BranchUserResponse(BranchUserBase):
    """استجابة ربط المستخدم بالفرع"""
    id: int
    joined_at: datetime
    
    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    """قائمة الفروع مع التصفح"""
    items: List[BranchResponse]
    total: int
    page: int
    size: int
    pages: int


class BranchInCompany(BaseModel):
    """فرع داخل شركة"""
    branch: BranchResponse
    is_main_branch: bool = False
    user_count: int = 0
    
    class Config:
        from_attributes = True


class CompanyBranches(BaseModel):
    """فروع الشركة"""
    company: BranchResponse
    branches: List[BranchInCompany]
    main_branch: Optional[BranchResponse] = None
    
    class Config:
        from_attributes = True
