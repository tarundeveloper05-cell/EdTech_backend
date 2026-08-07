from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.routes import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.exam_schema import ReportCardGenerate, ReportCardResponse
from app.services.report_card_service import report_card_service

router = APIRouter()


def _ensure_admin_or_teacher(current_user: User) -> None:
    if current_user.role.role_name not in ("ADMIN", "TEACHER"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or teacher users can perform this action",
        )


@router.post("/generate", response_model=ReportCardResponse)
async def generate_report_card(
    payload: ReportCardGenerate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin_or_teacher(current_user)
    return await report_card_service.generate_report_card(
        session, payload.student_id, payload.exam_id, payload.remarks
    )


@router.get("/{report_card_id}", response_model=ReportCardResponse)
async def get_report_card(
    report_card_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await report_card_service.get_report_card(session, report_card_id)
