from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClassCreate(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=100)
    section: str = Field(..., min_length=1, max_length=50)
    academic_year: str = Field(..., min_length=1, max_length=20)
    class_teacher_id: Optional[UUID] = None


class ClassUpdate(BaseModel):
    class_name: Optional[str] = Field(None, min_length=1, max_length=100)
    section: Optional[str] = Field(None, min_length=1, max_length=50)
    academic_year: Optional[str] = Field(None, min_length=1, max_length=20)
    class_teacher_id: Optional[UUID] = None


class ClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    class_name: str
    section: str
    academic_year: str
    class_teacher_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class ClassSubjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_name: str


class ClassTeacherSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: str
