from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_model import Class
from app.repositories.exam_repository import exam_repository
from app.services.crud_service import CRUDService


class ExamService(CRUDService):
    async def create(self, session: AsyncSession, data: dict):
        await self._validate_exam(session, data)
        item = await self.repository.create(session, data)
        await session.commit()
        return item

    async def update(self, session: AsyncSession, item_id: UUID, data: dict):
        item = await self.get(session, item_id)
        merged = {
            "exam_name": item.exam_name,
            "exam_type": item.exam_type,
            "class_id": item.class_id,
            "start_date": item.start_date,
            "end_date": item.end_date,
            "max_marks": item.max_marks,
        }
        merged.update(data)
        await self._validate_exam(session, merged)
        item = await self.repository.update(session, item, data)
        await session.commit()
        return item

    async def _validate_exam(self, session: AsyncSession, data: dict) -> None:
        if data["start_date"] > data["end_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be before or equal to end_date",
            )
        if data["max_marks"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_marks must be greater than 0",
            )
        if await session.get(Class, data["class_id"]) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found",
            )


exam_service = ExamService(exam_repository, "Exam")
