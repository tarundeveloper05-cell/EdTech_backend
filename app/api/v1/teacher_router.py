from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router_factory import build_crud_router
from app.core.database import get_db
from app.models.class_model import Class
from app.models.subject_model import Subject
from app.models.teacher_subject_model import TeacherSubject
from app.schemas.class_schema import ClassResponse
from app.schemas.subject_schema import SubjectResponse
from app.schemas.teacher_schema import TeacherCreate, TeacherResponse, TeacherUpdate
from app.services.teacher_service import teacher_service

router = build_crud_router(teacher_service, TeacherCreate, TeacherUpdate, TeacherResponse)


@router.get("/{teacher_id}/classes", response_model=list[ClassResponse])
async def get_classes_by_teacher(
    teacher_id: UUID, session: AsyncSession = Depends(get_db)
):
    await teacher_service.get(session, teacher_id)
    result = await session.execute(
        select(Class)
        .join(TeacherSubject, TeacherSubject.class_id == Class.id)
        .where(TeacherSubject.teacher_id == teacher_id)
        .distinct()
    )
    return result.scalars().all()


@router.get("/{teacher_id}/subjects", response_model=list[SubjectResponse])
async def get_subjects_by_teacher(
    teacher_id: UUID, session: AsyncSession = Depends(get_db)
):
    await teacher_service.get(session, teacher_id)
    result = await session.execute(
        select(Subject)
        .join(TeacherSubject, TeacherSubject.subject_id == Subject.id)
        .where(TeacherSubject.teacher_id == teacher_id)
        .distinct()
    )
    return result.scalars().all()
