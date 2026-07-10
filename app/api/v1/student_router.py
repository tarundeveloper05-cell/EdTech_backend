from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router_factory import build_crud_router
from app.core.database import get_db
from app.models.exam_result_model import ExamResult
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentUpdate
from app.schemas.exam_schema import (
    ExamResultResponse,
    ReportCardResponse,
    StudentPerformanceSummary,
)
from app.services.report_card_service import report_card_service
from app.services.student_service import student_service

router = build_crud_router(student_service, StudentCreate, StudentUpdate, StudentResponse)


@router.get("/{student_id}/exam-results", response_model=list[ExamResultResponse])
async def get_student_exam_results(
    student_id: UUID, session: AsyncSession = Depends(get_db)
):
    await student_service.get(session, student_id)
    result = await session.execute(
        select(ExamResult).where(ExamResult.student_id == student_id)
    )
    return result.scalars().all()


@router.get("/{student_id}/report-cards", response_model=list[ReportCardResponse])
async def get_student_report_cards(
    student_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await report_card_service.get_student_report_cards(session, student_id)


@router.get("/{student_id}/performance", response_model=StudentPerformanceSummary)
async def get_student_performance(
    student_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await report_card_service.get_performance_summary(session, student_id)
