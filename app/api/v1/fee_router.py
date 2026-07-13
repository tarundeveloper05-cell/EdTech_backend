from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.fee_schema import FeeInvoiceCreate, FeeInvoiceResponse, FeeInvoiceUpdate, FeeStructureCreate, FeeStructureResponse, FeeStructureUpdate, FeeSummaryResponse, PaymentCreate, PaymentResponse, PaymentUpdate
from app.services.fee_service import fee_invoice_service, fee_structure_service, payment_service

fee_structure_router = APIRouter()
@fee_structure_router.post("", response_model=FeeStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_fee_structure(payload: FeeStructureCreate, session: AsyncSession = Depends(get_db)): return await fee_structure_service.create(session, payload.model_dump())
@fee_structure_router.get("", response_model=list[FeeStructureResponse])
async def list_fee_structures(session: AsyncSession = Depends(get_db)): return await fee_structure_service.list(session)
@fee_structure_router.get("/{item_id}", response_model=FeeStructureResponse)
async def get_fee_structure(item_id: UUID, session: AsyncSession = Depends(get_db)): return await fee_structure_service.get(session, item_id)
@fee_structure_router.put("/{item_id}", response_model=FeeStructureResponse)
async def update_fee_structure(item_id: UUID, payload: FeeStructureUpdate, session: AsyncSession = Depends(get_db)): return await fee_structure_service.update(session, item_id, payload.model_dump(exclude_unset=True))
@fee_structure_router.delete("/{item_id}")
async def delete_fee_structure(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await fee_structure_service.delete(session, item_id); return {"message": "Deleted successfully"}

fee_invoice_router = APIRouter()
@fee_invoice_router.post("", response_model=FeeInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_fee_invoice(payload: FeeInvoiceCreate, session: AsyncSession = Depends(get_db)): return await fee_invoice_service.create(session, payload.model_dump())
@fee_invoice_router.get("", response_model=list[FeeInvoiceResponse])
async def list_fee_invoices(session: AsyncSession = Depends(get_db)): return await fee_invoice_service.list(session)
@fee_invoice_router.get("/{item_id}", response_model=FeeInvoiceResponse)
async def get_fee_invoice(item_id: UUID, session: AsyncSession = Depends(get_db)): return await fee_invoice_service.get(session, item_id)
@fee_invoice_router.put("/{item_id}", response_model=FeeInvoiceResponse)
async def update_fee_invoice(item_id: UUID, payload: FeeInvoiceUpdate, session: AsyncSession = Depends(get_db)): return await fee_invoice_service.update(session, item_id, payload.model_dump(exclude_unset=True))
@fee_invoice_router.delete("/{item_id}")
async def delete_fee_invoice(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await fee_invoice_service.delete(session, item_id); return {"message": "Deleted successfully"}
@fee_invoice_router.get("/{invoice_id}/payments", response_model=list[PaymentResponse])
async def invoice_payments(invoice_id: UUID, session: AsyncSession = Depends(get_db)): return await payment_service.get_by_invoice(session, invoice_id)

payment_router = APIRouter()
@payment_router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(payload: PaymentCreate, session: AsyncSession = Depends(get_db)): return await payment_service.create(session, payload.model_dump())
@payment_router.get("", response_model=list[PaymentResponse])
async def list_payments(session: AsyncSession = Depends(get_db)): return await payment_service.list(session)
@payment_router.get("/{item_id}", response_model=PaymentResponse)
async def get_payment(item_id: UUID, session: AsyncSession = Depends(get_db)): return await payment_service.get(session, item_id)
@payment_router.put("/{item_id}", response_model=PaymentResponse)
async def update_payment(item_id: UUID, payload: PaymentUpdate, session: AsyncSession = Depends(get_db)): return await payment_service.update(session, item_id, payload.model_dump(exclude_unset=True))
@payment_router.delete("/{item_id}")
async def delete_payment(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await payment_service.delete(session, item_id); return {"message": "Deleted successfully"}

student_fee_router = APIRouter()
@student_fee_router.get("/{student_id}/fee-invoices", response_model=list[FeeInvoiceResponse])
async def student_invoices(student_id: UUID, session: AsyncSession = Depends(get_db)): return await fee_invoice_service.get_by_student(session, student_id)
@student_fee_router.get("/{student_id}/payments", response_model=list[PaymentResponse])
async def student_payments(student_id: UUID, session: AsyncSession = Depends(get_db)): return await payment_service.get_by_student(session, student_id)
@student_fee_router.get("/{student_id}/outstanding-fees", response_model=list[FeeInvoiceResponse])
async def outstanding_fees(student_id: UUID, session: AsyncSession = Depends(get_db)):
    return [invoice for invoice in await fee_invoice_service.get_by_student(session, student_id) if invoice.status != "PAID"]
@student_fee_router.get("/{student_id}/fee-summary", response_model=FeeSummaryResponse)
async def fee_summary(student_id: UUID, session: AsyncSession = Depends(get_db)): return await payment_service.summary(session, student_id)
