from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report_card_model import ReportCard


class ReportCardRepository:
    async def create(self, session: AsyncSession, data: dict) -> ReportCard:
        report_card = ReportCard(**data)
        session.add(report_card)
        await session.flush()
        await session.refresh(report_card)
        return report_card

    async def get_by_id(self, session: AsyncSession, report_card_id: UUID):
        return await session.get(ReportCard, report_card_id)

    async def get_by_student(self, session: AsyncSession, student_id: UUID):
        result = await session.execute(
            select(ReportCard).where(ReportCard.student_id == student_id)
        )
        return list(result.scalars().all())

    async def get_by_exam(self, session: AsyncSession, exam_id: UUID):
        result = await session.execute(
            select(ReportCard).where(ReportCard.exam_id == exam_id)
        )
        return list(result.scalars().all())

    async def get_by_student_exam(
        self, session: AsyncSession, student_id: UUID, exam_id: UUID
    ):
        result = await session.execute(
            select(ReportCard).where(
                ReportCard.student_id == student_id,
                ReportCard.exam_id == exam_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, report_card: ReportCard, data: dict):
        for field, value in data.items():
            setattr(report_card, field, value)
        session.add(report_card)
        await session.flush()
        await session.refresh(report_card)
        return report_card


report_card_repository = ReportCardRepository()
