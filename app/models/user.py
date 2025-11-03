from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel
from app.models.associations import user_roles, tenant_user


class User(BaseModel):
    """
    نموذج المستخدم - محدث لدعم النظام متعدد المستأجرين
    يمكن للمستخدم الواحد أن يكون مرتبطاً بعدة شركات وفروع
    """
    __tablename__ = "users"
    
    # معلومات أساسية
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # معلومات شخصية
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(100), nullable=True)  # الاسم الكامل
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # حالة الحساب
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    is_superuser = Column(Boolean, default=False, index=True)
    
    # معلومات الأمان
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    
    # إعدادات المستخدم
    language = Column(String(10), nullable=True, default="ar")
    timezone = Column(String(50), nullable=True, default="Asia/Riyadh")
    theme = Column(String(20), nullable=True, default="light")  # light, dark
    
    # معلومات إضافية
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # التواريخ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # العلاقات - النظام متعدد المستأجرين
    
    # الشركة الأساسية (DEPRECATED - استخدم companies)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    tenant = relationship("Tenant", back_populates="users")
    
    # الشركات المرتبطة بالمستخدم
    companies = relationship("Tenant", secondary="tenant_user", back_populates="users")
    
    # الفروع المرتبطة بالمستخدم
    branches = relationship("Branch", secondary="branch_user", back_populates="users")
    
    # الأدوار الأساسية
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @property
    def display_name(self) -> str:
        """اسم العرض للمستخدم"""
        if self.full_name:
            return self.full_name
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def primary_company(self) -> str:
        """الشركة الأساسية للمستخدم"""
        return self.tenant

    def get_companies(self):
        """الحصول على جميع الشركات المرتبطة بالمستخدم"""
        return self.companies

    def get_branches(self, company_id: int = None):
        """الحصول على الفروع المرتبطة بالمستخدم"""
        if company_id:
            return [branch for branch in self.branches if branch.tenant_id == company_id]
        return self.branches

    def is_member_of_company(self, company_id: int) -> bool:
        """فحص ما إذا كان المستخدم عضواً في شركة معينة"""
        return any(company.id == company_id for company in self.companies)

    def is_member_of_branch(self, branch_id: int) -> bool:
        """فحص ما إذا كان المستخدم عضواً في فرع معين"""
        return any(branch.id == branch_id for branch in self.branches)

    def get_primary_branch(self, company_id: int = None):
        """الحصول على الفرع الأساسي للمستخدم"""
        primary_branches = []
        
        for branch in self.branches:
            if company_id and branch.tenant_id != company_id:
                continue
            
            # البحث عن الفرع الأساسي في جدول branch_user
            for branch_user in branch.__table__.c.branch_user.columns:
                # هنا نحتاج إلى query للفحص
                pass
        
        return primary_branches[0] if primary_branches else None

    def get_active_companies(self):
        """الحصول على الشركات النشطة"""
        return [company for company in self.companies if company.is_active]

    def get_active_branches(self):
        """الحصول على الفروع النشطة"""
        return [branch for branch in self.branches if branch.is_active]

    def has_role_in_company(self, company_id: int, role_name: str) -> bool:
        """فحص ما إذا كان المستخدم لديه دور معين في شركة معينة"""
        # سيتم تنفيذ هذا بعد إنشاء TenantUserRole service
        return False
