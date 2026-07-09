from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role_name: str
    description: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, max_length=20)
    status: bool = True
    role_id: UUID


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[bool] = None
    role_id: Optional[UUID] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    phone: Optional[str] = None
    status: bool
    last_login: Optional[datetime] = None
    role_id: UUID
    role: Optional[RoleResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
