from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.admission_model import AdmissionApplicationStatus


class AdmissionApplicationCreate(BaseModel):
    applicant_name: str = Field(..., min_length=1, max_length=255)
    applied_class: UUID
    application_date: date
    status: AdmissionApplicationStatus = AdmissionApplicationStatus.PENDING
    remarks: Optional[str] = None


class AdmissionApplicationUpdate(BaseModel):
    applicant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    applied_class: Optional[UUID] = None
    application_date: Optional[date] = None
    status: Optional[AdmissionApplicationStatus] = None
    remarks: Optional[str] = None


class AdmissionApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    applicant_name: str
    applied_class: UUID
    application_date: date
    status: AdmissionApplicationStatus
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AdmissionDocumentCreate(BaseModel):
    application_id: UUID
    document_type: str = Field(..., min_length=1, max_length=100)
    file_path: str = Field(..., min_length=1, max_length=500)
    verified: bool = False
    verified_by: Optional[UUID] = None
    verified_date: Optional[date] = None


class AdmissionDocumentUpdate(BaseModel):
    document_type: Optional[str] = Field(None, min_length=1, max_length=100)
    file_path: Optional[str] = Field(None, min_length=1, max_length=500)
    verified: Optional[bool] = None
    verified_by: Optional[UUID] = None
    verified_date: Optional[date] = None


class AdmissionDocumentVerify(BaseModel):
    verified_by: UUID
    verified_date: date


class AdmissionDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    document_type: str
    file_path: str
    verified: bool
    verified_by: Optional[UUID] = None
    verified_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class AdmissionSummaryResponse(BaseModel):
    total_applications: int
    pending: int
    approved: int
    rejected: int
