import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AdmissionApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AdmissionApplication(Base):
    __tablename__ = "admission_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    applicant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    applied_class: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False
    )
    application_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AdmissionApplicationStatus] = mapped_column(
        Enum(AdmissionApplicationStatus, name="admission_application_status"),
        nullable=False,
        default=AdmissionApplicationStatus.PENDING,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    class_ = relationship("Class", back_populates="admission_applications", lazy="selectin")
    documents = relationship(
        "AdmissionDocument",
        back_populates="application",
        cascade="all, delete-orphan",
    )


class AdmissionDocument(Base):
    __tablename__ = "admission_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("admission_applications.id"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    verified_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    application = relationship("AdmissionApplication", back_populates="documents", lazy="selectin")
    verifier = relationship(
        "User",
        back_populates="verified_documents",
        foreign_keys=[verified_by],
        lazy="selectin",
    )
