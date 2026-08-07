from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FeeStructureCreate(BaseModel):
    fee_type: str = Field(min_length=1, max_length=100)
    description: str | None = None
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    academic_year: str | None = Field(None, max_length=20)
    class_id: UUID | None = None
    section: str | None = Field(None, max_length=50)
    student_category_id: UUID | None = None
    is_active: bool = True
    is_mandatory: bool = True
    max_discount_percentage: Decimal | None = Field(None, max_digits=5, decimal_places=2, ge=0)
    tax_percentage: Decimal | None = Field(None, max_digits=5, decimal_places=2, ge=0)


class FeeStructureUpdate(BaseModel):
    fee_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    amount: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    academic_year: str | None = Field(None, max_length=20)
    class_id: UUID | None = None
    section: str | None = Field(None, max_length=50)
    student_category_id: UUID | None = None
    is_active: bool | None = None
    is_mandatory: bool | None = None
    max_discount_percentage: Decimal | None = Field(None, max_digits=5, decimal_places=2, ge=0)
    tax_percentage: Decimal | None = Field(None, max_digits=5, decimal_places=2, ge=0)


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
    amount: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    discount_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    late_fee_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    scholarship_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    net_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    status: str | None = None
    assignment_id: UUID | None = None


class FeeInvoiceUpdate(BaseModel):
    fee_type_id: UUID | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    amount: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    discount_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    late_fee_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    scholarship_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    net_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    status: str | None = None
    assignment_id: UUID | None = None


class FeeInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    student_id: UUID
    fee_type_id: UUID
    invoice_number: str | None = None
    invoice_date: date
    due_date: date
    amount: Decimal
    discount_amount: Decimal
    late_fee_amount: Decimal
    scholarship_amount: Decimal
    net_amount: Decimal | None = None
    status: str
    assignment_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class PaymentCreate(BaseModel):
    invoice_id: UUID
    payment_date: date
    amount_paid: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    payment_method: str
    payment_status: str | None = None
    transaction_no: str | None = Field(None, max_length=100)
    receipt_no: str | None = Field(None, max_length=100)
    receipt_number: str | None = None
    remarks: str | None = None


class PaymentUpdate(BaseModel):
    payment_date: date | None = None
    amount_paid: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    payment_method: str | None = None
    payment_status: str | None = None
    transaction_no: str | None = Field(None, max_length=100)
    receipt_no: str | None = Field(None, max_length=100)
    receipt_number: str | None = None
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


class FeeStructureDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    fee_type: str
    description: str | None = None
    amount: Decimal
    academic_year: str | None = None
    class_name: str | None = None
    class_id: UUID | None = None
    section: str | None = None
    student_category_id: UUID | None = None
    student_category_name: str | None = None
    is_active: bool
    is_mandatory: bool
    max_discount_percentage: Decimal | None = None
    tax_percentage: Decimal | None = None
    installments: list["FeeInstallmentResponse"]
    created_at: datetime
    updated_at: datetime


class FeeInstallmentCreate(BaseModel):
    fee_structure_id: UUID
    installment_number: int = Field(ge=1)
    due_date: date
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    is_locked: bool = False


class FeeInstallmentUpdate(BaseModel):
    installment_number: int | None = Field(None, ge=1)
    due_date: date | None = None
    amount: Decimal | None = Field(None, gt=0, max_digits=10, decimal_places=2)
    is_locked: bool | None = None


class FeeInstallmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    fee_structure_id: UUID
    installment_number: int
    due_date: date
    amount: Decimal
    is_locked: bool
    created_at: datetime
    updated_at: datetime


class StudentFeeAssignmentCreate(BaseModel):
    student_id: UUID
    fee_structure_id: UUID
    academic_year: str
    total_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    discount_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    scholarship_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    late_fee_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    net_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    due_date: date
    status: str | None = None
    student_category_id: UUID | None = None


class StudentFeeAssignmentUpdate(BaseModel):
    total_amount: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    discount_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    scholarship_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    late_fee_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    net_amount: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    due_date: date | None = None
    status: str | None = None


class StudentFeeAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    student_id: UUID
    fee_structure_id: UUID
    fee_type: str | None = None
    fee_structure_name: str | None = None
    academic_year: str
    total_amount: Decimal
    discount_amount: Decimal
    scholarship_amount: Decimal
    late_fee_amount: Decimal
    net_amount: Decimal
    due_date: date
    status: str
    student_category_id: UUID | None = None
    student_category_name: str | None = None
    created_at: datetime
    updated_at: datetime


class StudentLedgerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    student_id: UUID
    transaction_date: date
    description: str
    debit: Decimal
    credit: Decimal
    balance: Decimal
    transaction_type: str
    reference_id: UUID | None = None
    reference_type: str | None = None
    created_at: datetime


class StudentLedgerSummaryResponse(BaseModel):
    student_id: UUID
    student_name: str
    previous_balance: Decimal
    total_debit: Decimal
    total_credit: Decimal
    outstanding_balance: Decimal
    scholarships: Decimal
    late_fees: Decimal
    refunds: Decimal
    adjustments: Decimal


class StudentLedgerCreate(BaseModel):
    student_id: UUID
    transaction_date: date
    description: str
    debit: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    credit: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    transaction_type: str
    reference_id: UUID | None = None
    reference_type: str | None = None


class StudentLedgerUpdate(BaseModel):
    transaction_date: date | None = None
    description: str | None = None
    debit: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    credit: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)
    transaction_type: str | None = None
    reference_id: UUID | None = None
    reference_type: str | None = None
