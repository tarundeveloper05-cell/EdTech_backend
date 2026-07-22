from datetime import date
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func, select
from app.models.student_model import Student
from app.models.user import User
from app.models.hostel_model import HostelRoom
from app.models.hostel_operations_model import *
from app.repositories.hostel_operations_repository import *
from app.services.crud_service import CRUDService
def bad(s): raise HTTPException(400,s)
class VisitorService(CRUDService):
 async def create(self,s,d): await self.valid(s,d); return await super().create(s,d)
 async def update(self,s,i,d): x=await self.get(s,i); m={k:getattr(x,k) for k in ('student_id','approved_by','visitor_name','phone','check_in_time','check_out_time')};m.update(d);await self.valid(s,m);return await super().update(s,i,d)
 async def valid(self,s,d):
  if not d['visitor_name'].strip() or not d['phone'].strip(): bad('Visitor name and phone are required')
  if await s.get(Student,d['student_id']) is None: bad('Student must exist')
  if await s.get(User,d['approved_by']) is None: bad('Approver user must exist')
class HostelFeeInvoiceService(CRUDService):
 async def create(self,s,d):
  if d['due_date']<d['invoice_date']: bad('Due date cannot be before invoice date')
  if await s.get(Student,d['student_id']) is None or (fee:=await s.get(HostelFeeStructure,d['hostel_fee_id'])) is None: bad('Student and hostel fee structure must exist')
  d['amount']=d.get('amount') or fee.amount; d['status']=HostelInvoiceStatus.PENDING; return await super().create(s,d)
 async def list(self,s):
  xs=await super().list(s)
  for x in xs:
   if x.status==HostelInvoiceStatus.PENDING and x.due_date<date.today(): x.status=HostelInvoiceStatus.OVERDUE
  await s.commit(); return xs
class HostelPaymentService(CRUDService):
 async def create(self,s,d):
  invoice=await s.get(HostelFeeInvoice,d['invoice_id'])
  if invoice is None: bad('Invoice must exist')
  paid=await s.scalar(select(func.coalesce(func.sum(HostelPayment.amount_paid),0)).where(HostelPayment.invoice_id==invoice.id)) or Decimal('0')
  if paid+d['amount_paid']>invoice.amount: bad('Total payments cannot exceed invoice amount')
  item=await super().create(s,d)
  if paid+d['amount_paid']==invoice.amount: invoice.status=HostelInvoiceStatus.PAID; await s.commit()
  return item
class WorkOrderService(CRUDService):
 async def create(self,s,d):
  req=await s.get(MaintenanceRequest,d['request_id'])
  if req is None or await s.get(User,d['assigned_to']) is None: bad('Maintenance request and assignee must exist')
  req.status=MaintenanceStatus.IN_PROGRESS; return await super().create(s,d)
 async def complete(self,s,i):
  order=await self.get(s,i); order.status=WorkOrderStatus.COMPLETED; order.completed_date=date.today(); req=await s.get(MaintenanceRequest,order.request_id); req.status=MaintenanceStatus.RESOLVED; await s.commit(); await s.refresh(order); return order
visitor_service=VisitorService(visitor_repository,'Hostel visitor',foreign_keys={'student_id':Student,'approved_by':User})
hostel_fee_structure_service=CRUDService(hostel_fee_structure_repository,'Hostel fee structure',unique_constraints=(('fee_type','academic_year'),))
hostel_fee_invoice_service=HostelFeeInvoiceService(hostel_fee_invoice_repository,'Hostel fee invoice')
hostel_payment_service=HostelPaymentService(hostel_payment_repository,'Hostel payment')
mess_menu_service=CRUDService(mess_menu_repository,'Mess menu',unique_constraints=(('meal_type','menu_date'),),foreign_keys={'created_by':User})
mess_expense_service=CRUDService(mess_expense_repository,'Mess expense')
mess_collection_service=CRUDService(mess_collection_repository,'Mess collection',foreign_keys={'student_id':Student,'received_by':User})
mess_attendance_service=CRUDService(mess_attendance_repository,'Mess attendance',unique_constraints=(('student_id','meal_type','attendance_date'),),foreign_keys={'student_id':Student})
maintenance_request_service=CRUDService(maintenance_request_repository,'Maintenance request',foreign_keys={'requested_by':Student,'room_id':HostelRoom})
work_order_service=WorkOrderService(work_order_repository,'Work order')
