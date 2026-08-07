import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookIssueStatus(str, Enum):
    ISSUED = "ISSUED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class FinePaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    WAIVED = "WAIVED"


class BookCategory(Base):
    __tablename__ = "book_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    books: Mapped[list["Book"]] = relationship("Book", back_populates="category")


class Author(Base):
    __tablename__ = "library_authors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author_rel", cascade="all, delete-orphan")


class Publisher(Base):
    __tablename__ = "library_publishers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    contact_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    books: Mapped[list["Book"]] = relationship("Book", back_populates="publisher_rel", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    isbn: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("library_authors.id"), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publisher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("library_publishers.id"), nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("book_categories.id"), nullable=False)
    edition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rack_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shelf_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False)
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False)
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category: Mapped[BookCategory] = relationship("BookCategory", back_populates="books", lazy="selectin")
    author_rel: Mapped["Author | None"] = relationship("Author", back_populates="books", lazy="selectin")
    publisher_rel: Mapped["Publisher | None"] = relationship("Publisher", back_populates="books", lazy="selectin")
    book_issues: Mapped[list["BookIssue"]] = relationship("BookIssue", back_populates="book", cascade="all, delete-orphan")
    reservations: Mapped[list["BookReservation"]] = relationship("BookReservation", back_populates="book", cascade="all, delete-orphan")


class BookIssue(Base):
    __tablename__ = "book_issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fine_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0")
    fine_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=BookIssueStatus.ISSUED.value, server_default=BookIssueStatus.ISSUED.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book: Mapped[Book] = relationship("Book", back_populates="book_issues", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", back_populates="book_issues", lazy="selectin")
    fine_payments: Mapped[list["FinePayment"]] = relationship("FinePayment", back_populates="book_issue", cascade="all, delete-orphan")

    @property
    def book_title(self) -> str | None:
        return self.book.title if self.book else None

    @property
    def book_author(self) -> str | None:
        return self.book.author if self.book else None

    @property
    def student_name(self) -> str | None:
        if self.student:
            parts = [self.student.first_name, self.student.last_name]
            return " ".join(p for p in parts if p) or None
        return None

    @property
    def student_class(self) -> str | None:
        return self.student.class_name if self.student else None


class BookReservation(Base):
    __tablename__ = "book_reservations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    reservation_date: Mapped[date] = mapped_column(Date, nullable=False, default=func.now)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=ReservationStatus.PENDING.value, server_default=ReservationStatus.PENDING.value)
    approval_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book: Mapped[Book] = relationship("Book", back_populates="reservations", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")

    @property
    def book_title(self) -> str | None:
        return self.book.title if self.book else None

    @property
    def book_author(self) -> str | None:
        return self.book.author if self.book else None

    @property
    def student_name(self) -> str | None:
        if self.student:
            parts = [self.student.first_name, self.student.last_name]
            return " ".join(p for p in parts if p) or None
        return None

    @property
    def student_class(self) -> str | None:
        return self.student.class_name if self.student else None


class LibrarySettings(Base):
    __tablename__ = "library_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    max_books_per_student: Mapped[int] = mapped_column(Integer, nullable=False, default=5, server_default="5")
    fine_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("10.00"), server_default="10.00")
    reservation_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    borrow_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=14, server_default="14")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FinePayment(Base):
    __tablename__ = "fine_payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("book_issues.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0")
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=FinePaymentStatus.PENDING.value, server_default=FinePaymentStatus.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book_issue: Mapped[BookIssue] = relationship("BookIssue", back_populates="fine_payments", lazy="selectin")

    @property
    def book_title(self) -> str | None:
        return self.book_issue.book.title if self.book_issue and self.book_issue.book else None

    @property
    def student_name(self) -> str | None:
        if self.book_issue and self.book_issue.student:
            parts = [self.book_issue.student.first_name, self.book_issue.student.last_name]
            return " ".join(p for p in parts if p) or None
        return None
