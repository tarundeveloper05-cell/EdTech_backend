from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router_factory import build_crud_router
from app.core.database import get_db
from app.models.exam_result_model import ExamResult
from app.schemas.exam_schema import ExamResultResponse
from app.schemas.subject_schema import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services.subject_service import subject_service

router = build_crud_router(subject_service, SubjectCreate, SubjectUpdate, SubjectResponse)


@router.get("/{subject_id}/exam-results", response_model=list[ExamResultResponse])
async def get_subject_exam_results(
    subject_id: UUID, session: AsyncSession = Depends(get_db)
):
    await subject_service.get(session, subject_id)
    result = await session.execute(
        select(ExamResult).where(ExamResult.subject_id == subject_id)
    )
    return result.scalars().all()
