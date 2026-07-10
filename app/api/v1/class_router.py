from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router_factory import build_crud_router
from app.core.database import get_db
from app.models.class_subject_model import ClassSubject
from app.models.exam_model import Exam
from app.models.exam_result_model import ExamResult
from app.models.subject_model import Subject
from app.models.teacher_model import Teacher
from app.models.teacher_subject_model import TeacherSubject
from app.models.timetable_model import Timetable
from app.schemas.class_schema import (
    ClassCreate,
    ClassResponse,
    ClassSubjectSummary,
    ClassTeacherSummary,
    ClassUpdate,
)
from app.schemas.exam_schema import ExamResultResponse
from app.schemas.timetable_schema import TimetableResponse
from app.services.class_service import class_service

router = build_crud_router(class_service, ClassCreate, ClassUpdate, ClassResponse)


@router.get("/{class_id}/subjects", response_model=list[ClassSubjectSummary])
async def get_subjects_for_class(
    class_id: UUID, session: AsyncSession = Depends(get_db)
):
    await class_service.get(session, class_id)
    result = await session.execute(
        select(Subject)
        .join(ClassSubject, ClassSubject.subject_id == Subject.id)
        .where(ClassSubject.class_id == class_id)
    )
    return result.scalars().all()


@router.get("/{class_id}/exam-results", response_model=list[ExamResultResponse])
async def get_class_exam_results(
    class_id: UUID, session: AsyncSession = Depends(get_db)
):
    await class_service.get(session, class_id)
    result = await session.execute(
        select(ExamResult)
        .join(Exam, ExamResult.exam_id == Exam.id)
        .where(Exam.class_id == class_id)
    )
    return result.scalars().all()


@router.get("/{class_id}/teachers", response_model=list[ClassTeacherSummary])
async def get_teachers_for_class(
    class_id: UUID, session: AsyncSession = Depends(get_db)
):
    await class_service.get(session, class_id)
    result = await session.execute(
        select(Teacher)
        .join(TeacherSubject, TeacherSubject.teacher_id == Teacher.id)
        .where(TeacherSubject.class_id == class_id)
        .distinct()
    )
    return result.scalars().all()


@router.get("/{class_id}/timetable", response_model=list[TimetableResponse])
async def get_timetable_for_class(
    class_id: UUID, session: AsyncSession = Depends(get_db)
):
    await class_service.get(session, class_id)
    result = await session.execute(
        select(Timetable).where(Timetable.class_id == class_id)
    )
    return result.scalars().all()
