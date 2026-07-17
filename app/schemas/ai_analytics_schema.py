from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIAnalyticsCreate(BaseModel):
    student_id: UUID
    attendance_risk: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    performance_risk: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    predicted_grade: str | None = Field(None, max_length=10)
    learning_pattern: str | None = None
    recommendation: str | None = None
    generated_on: datetime | None = None


class AIAnalyticsResponse(AIAnalyticsCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    generated_on: datetime
    created_at: datetime
    updated_at: datetime


class AIChatHistoryCreate(BaseModel):
    user_id: UUID
    question: str = Field(min_length=1)
    response: str = Field(min_length=1)
    timestamp: datetime | None = None


class AIChatHistoryUpdate(BaseModel):
    question: str | None = Field(None, min_length=1)
    response: str | None = Field(None, min_length=1)


class AIChatHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    question: str
    response: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
