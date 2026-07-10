from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_model import Class
from app.models.class_subject_model import ClassSubject
from app.models.exam_model import Exam
from app.models.exam_result_model import ExamResult
from app.models.student_model import Student
from app.models.subject_model import Subject
from app.repositories.exam_result_repository import exam_result_repository
from app.services.crud_service import CRUDService


class ExamResultService(CRUDService):
    async def create(self, session: AsyncSession, data: dict):
        exam = await self._validate_result(session, data)
        await self._validate_duplicate(session, data)
        data["grade"] = self._calculate_grade(data["marks_obtained"], exam.max_marks)
        item = await self.repository.create(session, data)
        await session.commit()
        return item

    async def update(self, session: AsyncSession, item_id: UUID, data: dict):
        item = await self.get(session, item_id)
        exam = await session.get(Exam, item.exam_id)
        if "marks_obtained" in data:
            if data["marks_obtained"] < 0 or data["marks_obtained"] > exam.max_marks:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="marks_obtained must be between 0 and exam max_marks",
                )
            data["grade"] = self._calculate_grade(data["marks_obtained"], exam.max_marks)
        item = await self.repository.update(session, item, data)
        await session.commit()
        return item

    async def _validate_result(self, session: AsyncSession, data: dict) -> Exam:
        exam = await session.get(Exam, data["exam_id"])
        if exam is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
        student = await session.get(Student, data["student_id"])
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        if await session.get(Subject, data["subject_id"]) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        if student.class_id != exam.class_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student does not belong to exam class",
            )
        class_subject = (
            await session.execute(
                select(ClassSubject).where(
                    ClassSubject.class_id == exam.class_id,
                    ClassSubject.subject_id == data["subject_id"],
                )
            )
        ).scalar_one_or_none()
        if class_subject is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject does not belong to exam class",
            )
        if data["marks_obtained"] < 0 or data["marks_obtained"] > exam.max_marks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="marks_obtained must be between 0 and exam max_marks",
            )
        return exam

    async def _validate_duplicate(self, session: AsyncSession, data: dict) -> None:
        existing = await self.repository.get_by_fields(
            session,
            {
                "exam_id": data["exam_id"],
                "student_id": data["student_id"],
                "subject_id": data["subject_id"],
            },
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Result already exists for this exam, student and subject",
            )

    def _calculate_grade(self, marks: Decimal, max_marks: int) -> str:
        percentage = (Decimal(marks) / Decimal(max_marks)) * Decimal("100")
        if percentage >= 90:
            return "A+"
        if percentage >= 80:
            return "A"
        if percentage >= 70:
            return "B+"
        if percentage >= 60:
            return "B"
        if percentage >= 50:
            return "C"
        if percentage >= 40:
            return "D"
        return "F"


exam_result_service = ExamResultService(exam_result_repository, "ExamResult")
