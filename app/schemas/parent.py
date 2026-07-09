from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ParentBase(BaseModel):
    occupation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class ParentCreate(ParentBase):
    user_id: UUID


class ParentUpdate(BaseModel):
    user_id: Optional[UUID] = None
    occupation: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class ParentResponse(ParentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
