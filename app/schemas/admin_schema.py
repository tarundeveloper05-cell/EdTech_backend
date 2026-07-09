from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AdminCreate(BaseModel):
    user_id: UUID
    admin_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class AdminUpdate(BaseModel):
    user_id: Optional[UUID] = None
    admin_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    admin_name: str
    phone: Optional[str] = None
