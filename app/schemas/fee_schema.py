from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class FeeStructureCreate(BaseModel):
    fee_type: str = Field(min_length=1, max_length=100)
    description: str | None = None
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
class FeeStructureUpdate(BaseModel):
    fee_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    amount: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
class FeeStructureResponse(FeeStructureCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class FeeInvoiceCreate(BaseModel):
    student_id: UUID
    fee_type_id: UUID
    invoice_date: date
    due_date: date
    amount: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    status: str | None = None
class FeeInvoiceUpdate(BaseModel):
    fee_type_id: UUID | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    amount: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    status: str | None = None
class FeeInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    student_id: UUID
    fee_type_id: UUID
    invoice_date: date
    due_date: date
    amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime


class PaymentCreate(BaseModel):
    invoice_id: UUID
    payment_date: date
    amount_paid: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    payment_method: str
    transaction_no: str | None = Field(None, max_length=100)
    receipt_no: str | None = Field(None, max_length=100)
    remarks: str | None = None
class PaymentUpdate(BaseModel):
    payment_date: date | None = None
    amount_paid: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    payment_method: str | None = None
    transaction_no: str | None = Field(None, max_length=100)
    receipt_no: str | None = Field(None, max_length=100)
    remarks: str | None = None
class PaymentResponse(PaymentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class FeeSummaryResponse(BaseModel):
    student_id: UUID
    total_fees: Decimal
    paid: Decimal
    pending: Decimal
