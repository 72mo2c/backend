from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import BaseModel

# Association tables for many-to-many relationships

user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions", 
    BaseModel.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

# Multi-tenant association tables

tenant_user = Table(
    "tenant_user",
    BaseModel.metadata,
    Column("tenant_id", Integer, ForeignKey("tenants.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)

branch_user = Table(
    "branch_user",
    BaseModel.metadata,
    Column("branch_id", Integer, ForeignKey("branches.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)