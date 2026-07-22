from uuid import UUID
from fastapi import APIRouter,Depends,status
from sqlalchemy import func,select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.hostel_operations_schema import HostelFeeInvoiceCreate, HostelFeeInvoiceResponse, HostelFeeStructureCreate, HostelFeeStructureResponse, HostelPaymentCreate, HostelPaymentResponse, HostelVisitorCreate, HostelVisitorResponse, HostelVisitorUpdate, MaintenanceRequestCreate, MaintenanceRequestResponse, MessAttendanceCreate, MessAttendanceResponse, MessCollectionCreate, MessCollectionResponse, MessExpenseCreate, MessExpenseResponse, MessMenuCreate, MessMenuResponse, WorkOrderCreate, WorkOrderResponse
from app.models.hostel_operations_model import HostelFeeInvoice, HostelPayment, HostelVisitor, MaintenanceRequest, MessAttendance, MessCollection, MessExpense, WorkOrder
from app.services.hostel_operations_service import hostel_fee_invoice_service, hostel_fee_structure_service, hostel_payment_service, visitor_service, maintenance_request_service, mess_attendance_service, mess_collection_service, mess_expense_service, mess_menu_service, work_order_service
def crud(prefix,create,response,service):
 r=APIRouter()
 @r.post('',response_model=response,status_code=status.HTTP_201_CREATED)
 async def create_item(p:create,s:AsyncSession=Depends(get_db)): return await service.create(s,p.model_dump())
 @r.get('',response_model=list[response])
 async def list_items(s:AsyncSession=Depends(get_db)): return await service.list(s)
 return r
visitor_router=crud('',HostelVisitorCreate,HostelVisitorResponse,visitor_service)
@visitor_router.get('/{item_id}',response_model=HostelVisitorResponse)
async def visitor_get(item_id:UUID,s:AsyncSession=Depends(get_db)): return await visitor_service.get(s,item_id)
@visitor_router.put('/{item_id}',response_model=HostelVisitorResponse)
async def visitor_put(item_id:UUID,p:HostelVisitorUpdate,s:AsyncSession=Depends(get_db)): return await visitor_service.update(s,item_id,p.model_dump(exclude_unset=True))
@visitor_router.delete('/{item_id}')
async def visitor_del(item_id:UUID,s:AsyncSession=Depends(get_db)): await visitor_service.delete(s,item_id);return {'message':'Deleted successfully'}
fee_structure_router=crud('',HostelFeeStructureCreate,HostelFeeStructureResponse,hostel_fee_structure_service); fee_invoice_router=crud('',HostelFeeInvoiceCreate,HostelFeeInvoiceResponse,hostel_fee_invoice_service); hostel_payment_router=crud('',HostelPaymentCreate,HostelPaymentResponse,hostel_payment_service)
mess_menu_router=crud('',MessMenuCreate,MessMenuResponse,mess_menu_service); mess_expense_router=crud('',MessExpenseCreate,MessExpenseResponse,mess_expense_service); mess_collection_router=crud('',MessCollectionCreate,MessCollectionResponse,mess_collection_service); mess_attendance_router=crud('',MessAttendanceCreate,MessAttendanceResponse,mess_attendance_service)
maintenance_router=crud('',MaintenanceRequestCreate,MaintenanceRequestResponse,maintenance_request_service); work_order_router=crud('',WorkOrderCreate,WorkOrderResponse,work_order_service)
@work_order_router.post('/{item_id}/complete',response_model=WorkOrderResponse)
async def complete(item_id:UUID,s:AsyncSession=Depends(get_db)): return await work_order_service.complete(s,item_id)
student_hostel_extra_router=APIRouter()
@student_hostel_extra_router.get('/{student_id}/visitors',response_model=list[HostelVisitorResponse])
async def visitors(student_id:UUID,s:AsyncSession=Depends(get_db)): return list((await s.execute(select(HostelVisitor).where(HostelVisitor.student_id==student_id))).scalars())
@student_hostel_extra_router.get('/{student_id}/hostel-fees',response_model=list[HostelFeeInvoiceResponse])
async def fees(student_id:UUID,s:AsyncSession=Depends(get_db)): return list((await s.execute(select(HostelFeeInvoice).where(HostelFeeInvoice.student_id==student_id))).scalars())
@student_hostel_extra_router.get('/{student_id}/mess-attendance',response_model=list[MessAttendanceResponse])
async def attendance(student_id:UUID,s:AsyncSession=Depends(get_db)): return list((await s.execute(select(MessAttendance).where(MessAttendance.student_id==student_id))).scalars())
hostel_extra_router=APIRouter()
@hostel_extra_router.get('/fee-summary')
async def fee_summary(s:AsyncSession=Depends(get_db)): return {'total_invoiced':await s.scalar(select(func.coalesce(func.sum(HostelFeeInvoice.amount),0))) or 0,'total_collected':await s.scalar(select(func.coalesce(func.sum(HostelPayment.amount_paid),0))) or 0}
@hostel_extra_router.get('/mess/dashboard')
async def mess_dashboard(s:AsyncSession=Depends(get_db)): return {'total_collections':await s.scalar(select(func.coalesce(func.sum(MessCollection.amount),0))) or 0,'total_expenses':await s.scalar(select(func.coalesce(func.sum(MessExpense.amount),0))) or 0,'profit_loss':(await s.scalar(select(func.coalesce(func.sum(MessCollection.amount),0))) or 0)-(await s.scalar(select(func.coalesce(func.sum(MessExpense.amount),0))) or 0),'today_attendance':await s.scalar(select(func.count(MessAttendance.id)).where(MessAttendance.attendance_date==__import__('datetime').date.today(),MessAttendance.status=='PRESENT')) or 0}
@hostel_extra_router.get('/maintenance/dashboard')
async def maintenance_dashboard(s:AsyncSession=Depends(get_db)): return {'open_requests':await s.scalar(select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.status=='OPEN')) or 0,'in_progress_requests':await s.scalar(select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.status=='IN_PROGRESS')) or 0,'resolved_requests':await s.scalar(select(func.count(MaintenanceRequest.id)).where(MaintenanceRequest.status=='RESOLVED')) or 0,'completed_work_orders':await s.scalar(select(func.count(WorkOrder.id)).where(WorkOrder.status=='COMPLETED')) or 0}
