from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.fee_model import FeeInvoice, FeeStructure, Payment
from app.repositories.crud_repository import CRUDRepository


class FeeStructureRepository(CRUDRepository[FeeStructure]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_all(self, session: AsyncSession): return await self.list(session)


class FeeInvoiceRepository(CRUDRepository[FeeInvoice]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_all(self, session: AsyncSession): return await self.list(session)
    async def get_by_student(self, session: AsyncSession, student_id: UUID):
        return list((await session.execute(select(FeeInvoice).where(FeeInvoice.student_id == student_id))).scalars().all())


class PaymentRepository(CRUDRepository[Payment]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_all(self, session: AsyncSession): return await self.list(session)
    async def get_by_invoice(self, session: AsyncSession, invoice_id: UUID):
        return list((await session.execute(select(Payment).where(Payment.invoice_id == invoice_id))).scalars().all())


fee_structure_repository = FeeStructureRepository(FeeStructure)
fee_invoice_repository = FeeInvoiceRepository(FeeInvoice)
payment_repository = PaymentRepository(Payment)
