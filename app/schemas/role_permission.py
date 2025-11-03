from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    is_system_role: bool
    is_active: bool
    permissions: List[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleAssignment(BaseModel):
    user_id: int
    role_ids: List[int]


class RoleWithUsers(RoleResponse):
    user_count: int


class RoleList(BaseModel):
    roles: list[RoleResponse]
    total: int
    page: int
    per_page: int
