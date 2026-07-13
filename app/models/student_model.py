import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    admission_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    class_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    class_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True
    )
    roll_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    photo: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user = relationship("User", back_populates="student", lazy="selectin")
    class_ = relationship("Class", back_populates="students", lazy="selectin")
    attendance_records = relationship(
        "Attendance", back_populates="student", cascade="all, delete-orphan"
    )
    exam_results = relationship(
        "ExamResult", back_populates="student", cascade="all, delete-orphan"
    )
    report_cards = relationship(
        "ReportCard", back_populates="student", cascade="all, delete-orphan"
    )
    parent_students = relationship(
        "ParentStudent", back_populates="student", cascade="all, delete-orphan"
    )
    parents = relationship(
        "Parent",
        secondary="parent_students",
        back_populates="students",
        viewonly=True,
    )
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student", cascade="all, delete-orphan")
    fee_invoices = relationship("FeeInvoice", back_populates="student", cascade="all, delete-orphan")
