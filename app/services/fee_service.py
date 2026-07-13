from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fee_model import FeeInvoice, FeeStructure, Payment
from app.models.student_model import Student
from app.repositories.fee_repository import fee_invoice_repository, fee_structure_repository, payment_repository
from app.services.crud_service import CRUDService

INVOICE_STATUSES = {"PAID", "UNPAID", "OVERDUE"}
PAYMENT_METHODS = {"CASH", "CARD", "UPI", "BANK_TRANSFER", "ONLINE"}


class FeeStructureService(CRUDService):
    async def create(self, session, data):
        await self._validate_amount(data)
        return await super().create(session, data)
    async def update(self, session, item_id, data):
        await self._validate_amount(data)
        return await super().update(session, item_id, data)
    async def _validate_amount(self, data):
        if data.get("amount") is not None and data["amount"] <= 0:
            raise HTTPException(status_code=400, detail="amount must be greater than 0")


class FeeInvoiceService(CRUDService):
    async def create(self, session, data):
        await self._validate_invoice(session, data)
        if data.get("amount") is None:
            data["amount"] = (await session.get(FeeStructure, data["fee_type_id"])).amount
        data.setdefault("status", "UNPAID")
        return await super().create(session, data)

    async def update(self, session, item_id, data):
        item = await self.get(session, item_id)
        merged = {field: getattr(item, field) for field in ("student_id", "fee_type_id", "invoice_date", "due_date", "amount", "status")}
        merged.update(data)
        await self._validate_invoice(session, merged)
        updated = await super().update(session, item_id, data)
        await self._set_invoice_status(session, updated)
        return updated

    async def get(self, session, item_id):
        item = await super().get(session, item_id)
        await self._set_invoice_status(session, item)
        return item

    async def list(self, session):
        items = await super().list(session)
        for item in items:
            await self._set_invoice_status(session, item)
        return items

    async def _validate_invoice(self, session, data):
        if data["due_date"] < data["invoice_date"]:
            raise HTTPException(status_code=400, detail="due_date cannot be before invoice_date")
        if await session.get(Student, data["student_id"]) is None:
            raise HTTPException(status_code=400, detail="Student must exist")
        if await session.get(FeeStructure, data["fee_type_id"]) is None:
            raise HTTPException(status_code=400, detail="Fee type must exist")
        if data.get("amount") is not None and data["amount"] <= 0:
            raise HTTPException(status_code=400, detail="amount must be greater than 0")
        if data.get("status") is not None and data["status"] not in INVOICE_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid invoice status")

    async def _set_invoice_status(self, session, invoice):
        total_paid = await _invoice_total_paid(session, invoice.id)
        invoice.status = "PAID" if total_paid == invoice.amount else "OVERDUE" if date.today() > invoice.due_date else "UNPAID"
        session.add(invoice)
        await session.commit()
        await session.refresh(invoice)

    async def get_by_student(self, session, student_id):
        if await session.get(Student, student_id) is None:
            raise HTTPException(status_code=404, detail="Student not found")
        items = await self.repository.get_by_student(session, student_id)
        for item in items:
            await self._set_invoice_status(session, item)
        return items


class PaymentService(CRUDService):
    async def create(self, session, data):
        invoice = await self._validate_payment(session, data)
        item = await super().create(session, data)
        await fee_invoice_service._set_invoice_status(session, invoice)
        return item

    async def update(self, session, item_id, data):
        item = await self.get(session, item_id)
        merged = {"invoice_id": item.invoice_id, "amount_paid": item.amount_paid, "payment_method": item.payment_method}
        merged.update(data)
        invoice = await self._validate_payment(session, merged, exclude_payment_id=item_id)
        updated = await super().update(session, item_id, data)
        await fee_invoice_service._set_invoice_status(session, invoice)
        return updated

    async def delete(self, session, item_id):
        item = await self.get(session, item_id)
        invoice = await session.get(FeeInvoice, item.invoice_id)
        await super().delete(session, item_id)
        await fee_invoice_service._set_invoice_status(session, invoice)

    async def _validate_payment(self, session, data, exclude_payment_id=None):
        invoice = await session.get(FeeInvoice, data["invoice_id"])
        if invoice is None:
            raise HTTPException(status_code=400, detail="Invoice must exist")
        if data["amount_paid"] <= 0:
            raise HTTPException(status_code=400, detail="amount_paid must be greater than 0")
        if data["payment_method"] not in PAYMENT_METHODS:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        total_paid = await _invoice_total_paid(session, invoice.id, exclude_payment_id)
        if total_paid + data["amount_paid"] > invoice.amount:
            raise HTTPException(status_code=400, detail="Total payments cannot exceed invoice amount")
        return invoice

    async def get_by_invoice(self, session, invoice_id):
        if await session.get(FeeInvoice, invoice_id) is None:
            raise HTTPException(status_code=404, detail="Fee invoice not found")
        return await self.repository.get_by_invoice(session, invoice_id)

    async def get_by_student(self, session, student_id):
        if await session.get(Student, student_id) is None:
            raise HTTPException(status_code=404, detail="Student not found")
        query = select(Payment).join(FeeInvoice).where(FeeInvoice.student_id == student_id)
        return list((await session.execute(query)).scalars().all())

    async def summary(self, session, student_id):
        invoices = await fee_invoice_service.get_by_student(session, student_id)
        total_fees = sum((invoice.amount for invoice in invoices), Decimal("0"))
        paid = Decimal("0")
        for invoice in invoices:
            paid += await _invoice_total_paid(session, invoice.id)
        return {"student_id": student_id, "total_fees": total_fees, "paid": paid, "pending": total_fees - paid}


async def _invoice_total_paid(session, invoice_id, exclude_payment_id=None):
    query = select(func.coalesce(func.sum(Payment.amount_paid), 0)).where(Payment.invoice_id == invoice_id)
    if exclude_payment_id is not None:
        query = query.where(Payment.id != exclude_payment_id)
    return (await session.execute(query)).scalar_one()


fee_structure_service = FeeStructureService(fee_structure_repository, "Fee structure", unique_fields=("fee_type",))
fee_invoice_service = FeeInvoiceService(fee_invoice_repository, "Fee invoice")
payment_service = PaymentService(payment_repository, "Payment")
