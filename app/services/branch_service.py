"""
خدمة إدارة الفروع (BranchService) للنظام متعدد المستأجرين
تدير عمليات CRUD للفروع مع التحكم في الصلاحيات
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from app.models.branch import Branch
from app.models.tenant import Tenant
from app.models.user import User
from app.models.associations import branch_user
from app.schemas.branch import BranchCreate, BranchUpdate, BranchResponse, BranchWithStats, BranchUsageStats


class BranchService:
    """خدمة إدارة الفروع"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_branches(
        self, 
        tenant_id: int,
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[Branch]:
        """الحصول على قائمة الفروع"""
        query = self.db.query(Branch).filter(Branch.tenant_id == tenant_id)
        
        if search:
            query = query.filter(
                or_(
                    Branch.name.contains(search),
                    Branch.code.contains(search),
                    Branch.city.contains(search),
                    Branch.country.contains(search),
                    Branch.manager_name.contains(search)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_branch(self, branch_id: int, tenant_id: int) -> Optional[Branch]:
        """الحصول على فرع محدد"""
        return self.db.query(Branch).filter(
            and_(
                Branch.id == branch_id,
                Branch.tenant_id == tenant_id
            )
        ).first()
    
    def get_branch_by_code(self, code: str, tenant_id: int) -> Optional[Branch]:
        """الحصول على فرع بالرمز"""
        return self.db.query(Branch).filter(
            and_(
                Branch.code == code,
                Branch.tenant_id == tenant_id
            )
        ).first()
    
    def create_branch(self, branch_data: BranchCreate, tenant_id: int) -> Branch:
        """إنشاء فرع جديد"""
        try:
            # التحقق من وجود الشركة
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if not tenant:
                raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
            
            # التحقق من وجود الرمز في نفس الشركة
            if self.get_branch_by_code(branch_data.code, tenant_id):
                raise ValueError(f"رمز الفرع '{branch_data.code}' موجود بالفعل في هذه الشركة")
            
            # التحقق من الحد الأقصى للفروع
            current_branches = self.db.query(Branch).filter(Branch.tenant_id == tenant_id).count()
            if current_branches >= tenant.max_branches:
                raise ValueError(f"تم الوصول للحد الأقصى للفروع ({tenant.max_branches}) لهذه الشركة")
            
            # إنشاء الفرع
            branch = Branch(
                tenant_id=tenant_id,
                name=branch_data.name,
                code=branch_data.code,
                description=branch_data.description,
                email=branch_data.email,
                phone=branch_data.phone,
                fax=branch_data.fax,
                address_line1=branch_data.address_line1,
                address_line2=branch_data.address_line2,
                city=branch_data.city,
                state=branch_data.state,
                postal_code=branch_data.postal_code,
                country=branch_data.country,
                branch_tax_number=branch_data.branch_tax_number,
                branch_registration_number=branch_data.branch_registration_number,
                manager_name=branch_data.manager_name,
                manager_email=branch_data.manager_email,
                manager_phone=branch_data.manager_phone,
                is_main_branch=branch_data.is_main_branch,
                currency=branch_data.currency,
                timezone=branch_data.timezone,
                language=branch_data.language,
                logo_url=branch_data.logo_url,
                is_active=branch_data.is_active,
                is_verified=branch_data.is_verified,
                opened_at=branch_data.opened_at
            )
            
            self.db.add(branch)
            self.db.commit()
            self.db.refresh(branch)
            
            return branch
            
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower():
                if "uq_branch_tenant_code" in str(e):
                    raise ValueError(f"رمز الفرع '{branch_data.code}' موجود بالفعل في هذه الشركة")
            raise ValueError("خطأ في إنشاء الفرع")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في إنشاء الفرع: {str(e)}")
    
    def update_branch(self, branch_id: int, branch_data: BranchUpdate, tenant_id: int) -> Optional[Branch]:
        """تحديث فرع"""
        branch = self.get_branch(branch_id, tenant_id)
        if not branch:
            raise ValueError(f"الفرع بالمعرف {branch_id} غير موجود")
        
        try:
            # تحديث البيانات
            update_data = branch_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(branch, field):
                    setattr(branch, field, value)
            
            branch.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(branch)
            
            return branch
            
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower():
                if "uq_branch_tenant_code" in str(e):
                    raise ValueError(f"رمز الفرع '{branch_data.code}' موجود بالفعل في هذه الشركة")
            raise ValueError("خطأ في تحديث الفرع")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في تحديث الفرع: {str(e)}")
    
    def delete_branch(self, branch_id: int, tenant_id: int) -> bool:
        """حذف فرع"""
        branch = self.get_branch(branch_id, tenant_id)
        if not branch:
            raise ValueError(f"الفرع بالمعرف {branch_id} غير موجود")
        
        try:
            self.db.delete(branch)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في حذف الفرع: {str(e)}")
    
    def get_branch_with_stats(self, branch_id: int, tenant_id: int) -> Optional[BranchWithStats]:
        """الحصول على فرع مع الإحصائيات"""
        branch = self.get_branch(branch_id, tenant_id)
        if not branch:
            return None
        
        # حساب الإحصائيات
        current_users = len(branch.users)
        current_account_books = len(branch.account_books)
        
        usage_stats = BranchUsageStats(
            current_users=current_users,
            current_account_books=current_account_books,
            is_active=branch.is_active,
            opened_date=branch.opened_at.isoformat() if branch.opened_at else None
        )
        
        branch_response = BranchResponse.from_orm(branch)
        return BranchWithStats(branch_response, usage_stats)
    
    def add_user_to_branch(self, branch_id: int, user_id: int, is_primary: bool = False) -> bool:
        """إضافة مستخدم للفرع"""
        # التحقق من وجود الفرع
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            raise ValueError(f"الفرع بالمعرف {branch_id} غير موجود")
        
        # التحقق من وجود المستخدم
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"المستخدم بالمعرف {user_id} غير موجود")
        
        # التحقق من عدم وجود الربط مسبقاً
        existing = self.db.query(branch_user).filter(
            and_(
                branch_user.c.branch_id == branch_id,
                branch_user.c.user_id == user_id
            )
        ).first()
        
        if existing:
            raise ValueError("المستخدم مرتبط بالفرع مسبقاً")
        
        try:
            # إضافة الربط (هذا مثال بسيط - في التطبيق الحقيقي تحتاج نموذج BranchUserLink)
            self.db.execute(
                branch_user.insert().values(branch_id=branch_id, user_id=user_id)
            )
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في إضافة المستخدم للفرع: {str(e)}")
    
    def remove_user_from_branch(self, branch_id: int, user_id: int) -> bool:
        """إزالة مستخدم من الفرع"""
        try:
            result = self.db.execute(
                branch_user.delete().where(
                    and_(
                        branch_user.c.branch_id == branch_id,
                        branch_user.c.user_id == user_id
                    )
                )
            )
            self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في إزالة المستخدم من الفرع: {str(e)}")
    
    def get_branch_users(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """الحصول على مستخدمي الفرع"""
        branch = self.db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            raise ValueError(f"الفرع بالمعرف {branch_id} غير موجود")
        
        return branch.users[skip:skip + limit]
    
    def get_main_branch(self, tenant_id: int) -> Optional[Branch]:
        """الحصول على الفرع الرئيسي"""
        return self.db.query(Branch).filter(
            and_(
                Branch.tenant_id == tenant_id,
                Branch.is_main_branch == True
            )
        ).first()
    
    def set_main_branch(self, branch_id: int, tenant_id: int) -> bool:
        """تعيين فرع رئيسي"""
        # التحقق من وجود الفرع
        branch = self.get_branch(branch_id, tenant_id)
        if not branch:
            raise ValueError(f"الفرع بالمعرف {branch_id} غير موجود")
        
        try:
            # إلغاء تعيين جميع الفروع الرئيسية الأخرى
            self.db.query(Branch).filter(
                and_(
                    Branch.tenant_id == tenant_id,
                    Branch.is_main_branch == True,
                    Branch.id != branch_id
                )
            ).update({Branch.is_main_branch: False})
            
            # تعيين هذا الفرع كرئيسي
            branch.is_main_branch = True
            branch.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"خطأ في تعيين الفرع الرئيسي: {str(e)}")
    
    def get_branches_count(self, tenant_id: int) -> int:
        """الحصول على عدد فروع الشركة"""
        return self.db.query(Branch).filter(Branch.tenant_id == tenant_id).count()
    
    def get_active_branches_count(self, tenant_id: int) -> int:
        """الحصول على عدد الفروع النشطة"""
        return self.db.query(Branch).filter(
            and_(
                Branch.tenant_id == tenant_id,
                Branch.is_active == True
            )
        ).count()
    
    def get_tenant_branches_summary(self, tenant_id: int) -> Dict[str, Any]:
        """ملخص فروع الشركة"""
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"الشركة بالمعرف {tenant_id} غير موجودة")
        
        branches = self.db.query(Branch).filter(Branch.tenant_id == tenant_id).all()
        active_branches = [b for b in branches if b.is_active]
        main_branch = self.get_main_branch(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant.name,
            "total_branches": len(branches),
            "active_branches": len(active_branches),
            "max_branches": tenant.max_branches,
            "usage_percentage": (len(branches) / tenant.max_branches * 100) if tenant.max_branches > 0 else 0,
            "main_branch": {
                "id": main_branch.id,
                "name": main_branch.name,
                "code": main_branch.code
            } if main_branch else None,
            "branches": [
                {
                    "id": branch.id,
                    "name": branch.name,
                    "code": branch.code,
                    "city": branch.city,
                    "country": branch.country,
                    "is_main_branch": branch.is_main_branch,
                    "is_active": branch.is_active,
                    "user_count": len(branch.users)
                }
                for branch in branches
            ]
        }
