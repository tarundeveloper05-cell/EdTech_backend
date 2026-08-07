from datetime import date
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import func, select
from app.models.student_model import Student
from app.models.user import User
from app.models.hostel_model import HostelAllocation, HostelRoom
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
class HostelComplaintService(CRUDService):
 async def create(self,s,d):
  if await s.get(Student,d['student_id']) is None: bad('Student must exist')
  d['resolution_status']=ComplaintStatus.OPEN; return await super().create(s,d)
 async def update(self,s,i,d):
  item=await self.get(s,i)
  if 'resolution_status' in d and d['resolution_status'] in (ComplaintStatus.RESOLVED,ComplaintStatus.CLOSED) and not d.get('resolution_notes'): bad('Resolution notes are required when closing a complaint')
  return await super().update(s,i,d)
 async def resolve(self,s,i,data):
  item=await self.get(s,i)
  item.resolution_status=ComplaintStatus.RESOLVED; item.resolution_notes=data.get('resolution_notes',''); item.resolved_by=data.get('resolved_by'); await s.commit(); await s.refresh(item); return item
class HostelNoticeService(CRUDService):
 async def create(self,s,d):
  if await s.get(User,d['published_by']) is None: bad('Publisher must be a valid user')
  d['status']=NoticeStatus.DRAFT; return await super().create(s,d)
 async def publish(self,s,i):
  item=await self.get(s,i)
  item.status=NoticeStatus.PUBLISHED; item.publish_date=date.today(); await s.commit(); await s.refresh(item); return item
 async def update(self,s,i,d):
  item=await self.get(s,i)
  if 'status' in d and d['status']==NoticeStatus.PUBLISHED and item.status!=NoticeStatus.PUBLISHED:
   item.publish_date=date.today()
  return await super().update(s,i,d)
 async def list_published(self,s):
  items=await self.list(s)
  today=date.today()
  for item in items:
   if item.status==NoticeStatus.PUBLISHED and item.expiry_date and item.expiry_date<today: item.status=NoticeStatus.EXPIRED
  await s.commit(); return items
class HostelSettingService(CRUDService):
 async def create(self,s,d):
  if await s.get(HostelSetting,d['setting_key']): bad('Setting key already exists')
  return await super().create(s,d)
 async def update(self,s,i,d):
  item=await self.get(s,i)
  if 'setting_key' in d and d['setting_key']!=item.setting_key:
   if await s.get(HostelSetting,d['setting_key']): bad('Setting key already exists')
  return await super().update(s,i,d)
class HostelLeaveRequestService(CRUDService):
 async def create(self,s,d):
  if await s.get(Student,d['student_id']) is None: bad('Student must exist')
  if await s.get(HostelAllocation,d['allocation_id']) is None: bad('Hostel allocation must exist')
  if d['start_date']>d['end_date']: bad('Start date cannot be after end date')
  d['approval_status']=LeaveApprovalStatus.PENDING; return await super().create(s,d)
 async def approve(self,s,i,data):
  item=await self.get(s,i)
  if item.approval_status!=LeaveApprovalStatus.PENDING: bad('Only pending leave requests can be approved')
  item.approval_status=LeaveApprovalStatus.APPROVED; item.approved_by=data.get('approved_by'); await s.commit(); await s.refresh(item); return item
 async def reject(self,s,i,data):
  item=await self.get(s,i)
  if item.approval_status!=LeaveApprovalStatus.PENDING: bad('Only pending leave requests can be rejected')
  item.approval_status=LeaveApprovalStatus.REJECTED; item.approved_by=data.get('approved_by'); await s.commit(); await s.refresh(item); return item
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
hostel_complaint_service=HostelComplaintService(hostel_complaint_repository,'Hostel complaint',foreign_keys={'student_id':Student,'assigned_to':User,'resolved_by':User})
hostel_notice_service=HostelNoticeService(hostel_notice_repository,'Hostel notice',foreign_keys={'published_by':User})
hostel_setting_service=HostelSettingService(hostel_setting_repository,'Hostel setting')
hostel_leave_request_service=HostelLeaveRequestService(hostel_leave_request_repository,'Hostel leave request',foreign_keys={'student_id':Student,'allocation_id':HostelAllocation,'approved_by':User})
