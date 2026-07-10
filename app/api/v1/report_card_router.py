from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.exam_schema import ReportCardGenerate, ReportCardResponse
from app.services.report_card_service import report_card_service

router = APIRouter()


@router.post("/generate", response_model=ReportCardResponse)
async def generate_report_card(
    payload: ReportCardGenerate, session: AsyncSession = Depends(get_db)
):
    return await report_card_service.generate_report_card(
        session, payload.student_id, payload.exam_id, payload.remarks
    )


@router.get("/{report_card_id}", response_model=ReportCardResponse)
async def get_report_card(
    report_card_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await report_card_service.get_report_card(session, report_card_id)
