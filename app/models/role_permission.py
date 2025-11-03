from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel
from app.models.associations import user_roles, role_permissions


class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    is_system_role = Column(Boolean, default=False)  # Core roles that can't be deleted
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(BaseModel):
    __tablename__ = "permissions"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., 'users', 'tenants'
    action = Column(String(50), nullable=False)  # e.g., 'create', 'read', 'update', 'delete'
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name})>"
