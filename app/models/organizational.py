from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Branch(BaseModel):
    __tablename__ = "branches"
    
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="branches")
    
    def __repr__(self):
        return f"<Branch(id={self.id}, name={self.name})>"
