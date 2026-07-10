from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.class_subject_model import ClassSubject
from app.models.exam_model import Exam
from app.models.exam_result_model import ExamResult
from app.models.report_card_model import ReportCard
from app.models.student_model import Student
from app.models.subject_model import Subject
from app.repositories.report_card_repository import report_card_repository


class ReportCardService:
    async def generate_report_card(
        self, session: AsyncSession, student_id: UUID, exam_id: UUID, remarks: str | None = None
    ):
        exam = await session.get(Exam, exam_id)
        if exam is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
        student = await session.get(Student, student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        if student.class_id != exam.class_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student does not belong to exam class",
            )

        subject_count = (
            await session.execute(
                select(func.count(ClassSubject.id)).where(ClassSubject.class_id == exam.class_id)
            )
        ).scalar_one()
        if subject_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam class has no subjects",
            )
        results = (
            await session.execute(
                select(ExamResult).where(
                    ExamResult.exam_id == exam_id,
                    ExamResult.student_id == student_id,
                )
            )
        ).scalars().all()

        total_marks = Decimal(exam.max_marks) * Decimal(subject_count)
        obtained_marks = sum((Decimal(result.marks_obtained) for result in results), Decimal("0"))
        percentage = (obtained_marks / total_marks * Decimal("100")).quantize(Decimal("0.01"))
        result_text = "PASS" if percentage >= Decimal("40") else "FAIL"
        data = {
            "student_id": student_id,
            "exam_id": exam_id,
            "total_marks": total_marks,
            "obtained_marks": obtained_marks,
            "percentage": percentage,
            "result": result_text,
            "remarks": remarks,
        }
        existing = await report_card_repository.get_by_student_exam(session, student_id, exam_id)
        if existing is None:
            report_card = await report_card_repository.create(session, data)
        else:
            report_card = await report_card_repository.update(session, existing, data)
        await self.calculate_rank(session, exam_id)
        await session.commit()
        await session.refresh(report_card)
        return report_card

    async def get_report_card(self, session: AsyncSession, report_card_id: UUID):
        report_card = await report_card_repository.get_by_id(session, report_card_id)
        if report_card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report card not found"
            )
        return report_card

    async def get_student_report_cards(self, session: AsyncSession, student_id: UUID):
        if await session.get(Student, student_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return await report_card_repository.get_by_student(session, student_id)

    async def calculate_rank(self, session: AsyncSession, exam_id: UUID) -> None:
        cards = await report_card_repository.get_by_exam(session, exam_id)
        cards.sort(key=lambda card: card.percentage, reverse=True)
        for index, card in enumerate(cards, start=1):
            card.rank = index
            session.add(card)
        await session.flush()

    async def get_toppers(self, session: AsyncSession, exam_id: UUID):
        cards = await report_card_repository.get_by_exam(session, exam_id)
        cards.sort(key=lambda card: card.rank or 999999)
        toppers = []
        for card in cards:
            student = await session.get(Student, card.student_id)
            name = " ".join(
                part for part in [student.first_name, student.last_name] if part
            ) or str(student.id)
            toppers.append(
                {"rank": card.rank or 0, "student_name": name, "percentage": card.percentage}
            )
        return toppers

    async def get_performance_summary(self, session: AsyncSession, student_id: UUID):
        cards = await self.get_student_report_cards(session, student_id)
        total_exams = len(cards)
        average = (
            round(sum(float(card.percentage) for card in cards) / total_exams, 2)
            if total_exams
            else 0
        )
        subject_totals = (
            await session.execute(
                select(
                    Subject.subject_name,
                    func.avg(ExamResult.marks_obtained).label("average_marks"),
                )
                .join(ExamResult, ExamResult.subject_id == Subject.id)
                .where(ExamResult.student_id == student_id)
                .group_by(Subject.subject_name)
            )
        ).all()
        best_subject = None
        worst_subject = None
        if subject_totals:
            best_subject = max(subject_totals, key=lambda row: row.average_marks).subject_name
            worst_subject = min(subject_totals, key=lambda row: row.average_marks).subject_name
        return {
            "student_id": student_id,
            "total_exams": total_exams,
            "average_percentage": average,
            "best_subject": best_subject,
            "worst_subject": worst_subject,
        }


report_card_service = ReportCardService()
