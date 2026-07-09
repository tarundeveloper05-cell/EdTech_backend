from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ParentStudentCreate(BaseModel):
    parent_id: UUID
    student_id: UUID
    relationship: Optional[str] = Field(None, max_length=50)


class ParentStudentUpdate(BaseModel):
    parent_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    relationship: Optional[str] = Field(None, max_length=50)


class ParentStudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_id: UUID
    student_id: UUID
    relationship: Optional[str] = None
