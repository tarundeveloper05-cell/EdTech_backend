from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router_factory import build_crud_router
from app.core.database import get_db
from app.schemas.exam_schema import ExamCreate, ExamResponse, ExamTopperResponse, ExamUpdate
from app.services.exam_service import exam_service
from app.services.report_card_service import report_card_service

router = build_crud_router(exam_service, ExamCreate, ExamUpdate, ExamResponse)


@router.get("/{exam_id}/toppers", response_model=list[ExamTopperResponse])
async def get_exam_toppers(exam_id: UUID, session: AsyncSession = Depends(get_db)):
    return await report_card_service.get_toppers(session, exam_id)
