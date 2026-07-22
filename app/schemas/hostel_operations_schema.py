from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.hostel_operations_model import HostelInvoiceStatus, MaintenancePriority, MaintenanceStatus, MessAttendanceStatus, WorkOrderStatus
class _Response(BaseModel): model_config=ConfigDict(from_attributes=True); id: UUID; created_at: datetime; updated_at: datetime
class HostelVisitorCreate(BaseModel): student_id: UUID; visitor_name: str=Field(min_length=1); relation: str|None=None; phone: str=Field(min_length=1); check_in_time: datetime; check_out_time: datetime|None=None; approved_by: UUID
class HostelVisitorUpdate(BaseModel): visitor_name: str|None=Field(None,min_length=1); relation: str|None=None; phone: str|None=Field(None,min_length=1); check_in_time: datetime|None=None; check_out_time: datetime|None=None; approved_by: UUID|None=None
class HostelVisitorResponse(HostelVisitorCreate,_Response): pass
class HostelFeeStructureCreate(BaseModel): fee_type: str=Field(min_length=1); amount: Decimal=Field(gt=0); academic_year: str=Field(min_length=1); description: str|None=None
class HostelFeeStructureResponse(HostelFeeStructureCreate,_Response): pass
class HostelFeeInvoiceCreate(BaseModel): student_id: UUID; hostel_fee_id: UUID; invoice_date: date; due_date: date; amount: Decimal|None=Field(None,gt=0)
class HostelFeeInvoiceResponse(_Response): student_id: UUID; hostel_fee_id: UUID; invoice_date: date; due_date: date; amount: Decimal; status: HostelInvoiceStatus
class HostelPaymentCreate(BaseModel): invoice_id: UUID; payment_date: date; amount_paid: Decimal=Field(gt=0); payment_method: str=Field(min_length=1); transaction_no: str|None=None; receipt_no: str|None=None; remarks: str|None=None
class HostelPaymentResponse(HostelPaymentCreate,_Response): pass
class MessMenuCreate(BaseModel): meal_type: str=Field(min_length=1); menu_date: date; breakfast: str|None=None; lunch: str|None=None; dinner: str|None=None; created_by: UUID
class MessMenuResponse(MessMenuCreate,_Response): pass
class MessExpenseCreate(BaseModel): expense_date: date; category: str=Field(min_length=1); description: str|None=None; amount: Decimal=Field(gt=0)
class MessExpenseResponse(MessExpenseCreate,_Response): pass
class MessCollectionCreate(BaseModel): student_id: UUID; amount: Decimal=Field(gt=0); collection_date: date; payment_method: str=Field(min_length=1); received_by: UUID
class MessCollectionResponse(MessCollectionCreate,_Response): pass
class MessAttendanceCreate(BaseModel): student_id: UUID; meal_type: str=Field(min_length=1); attendance_date: date; status: MessAttendanceStatus
class MessAttendanceResponse(MessAttendanceCreate,_Response): pass
class MaintenanceRequestCreate(BaseModel): requested_by: UUID; room_id: UUID; issue_type: str=Field(min_length=1); description: str=Field(min_length=1); priority: MaintenancePriority=MaintenancePriority.MEDIUM
class MaintenanceRequestResponse(_Response): requested_by: UUID; room_id: UUID; issue_type: str; description: str; priority: MaintenancePriority; status: MaintenanceStatus; requested_on: datetime
class WorkOrderCreate(BaseModel): request_id: UUID; assigned_to: UUID; scheduled_date: date
class WorkOrderResponse(_Response): request_id: UUID; assigned_to: UUID; scheduled_date: date; completed_date: date|None; status: WorkOrderStatus
