from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookCategoryCreate(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: bool | None = True


class BookCategoryUpdate(BaseModel):
    category_name: str | None = None
    description: str | None = None
    status: bool | None = None


class BookCategoryResponse(BookCategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    biography: str | None = None
    status: bool | None = True


class AuthorUpdate(BaseModel):
    name: str | None = None
    biography: str | None = None
    status: bool | None = None


class AuthorResponse(AuthorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class PublisherCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_info: str | None = None
    address: str | None = None
    status: bool | None = True


class PublisherUpdate(BaseModel):
    name: str | None = None
    contact_info: str | None = None
    address: str | None = None
    status: bool | None = None


class PublisherResponse(PublisherCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    subtitle: str | None = None
    author: str = Field(..., min_length=1, max_length=255)
    author_id: UUID | None = None
    publisher: str | None = None
    publisher_id: UUID | None = None
    category_id: UUID
    edition: str | None = None
    language: str | None = None
    rack_number: str | None = None
    shelf_number: str | None = None
    total_copies: int = Field(..., gt=0)
    available_copies: int = Field(..., ge=0)
    cover_image: str | None = None
    description: str | None = None
    status: bool | None = True


class BookUpdate(BaseModel):
    isbn: str | None = None
    title: str | None = None
    subtitle: str | None = None
    author: str | None = None
    author_id: UUID | None = None
    publisher: str | None = None
    publisher_id: UUID | None = None
    category_id: UUID | None = None
    edition: str | None = None
    language: str | None = None
    rack_number: str | None = None
    shelf_number: str | None = None
    total_copies: int | None = None
    available_copies: int | None = None
    cover_image: str | None = None
    description: str | None = None
    status: bool | None = None


class BookResponse(BookCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class BookIssueCreate(BaseModel):
    book_id: UUID
    student_id: UUID
    issue_date: date
    due_date: date


class BookIssueUpdate(BaseModel):
    issue_date: date | None = None
    due_date: date | None = None
    status: str | None = None
    fine_amount: Decimal | None = None
    fine_paid: bool | None = None


class BookIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    book_id: UUID
    student_id: UUID
    issue_date: date
    due_date: date
    return_date: date | None
    fine_amount: Decimal
    fine_paid: bool
    status: str
    created_at: datetime
    updated_at: datetime
    book_title: str | None = None
    book_author: str | None = None
    student_name: str | None = None
    student_class: str | None = None


class BookIssueResponseWithDetails(BookIssueResponse):
    pass


class BookReturnRequest(BaseModel):
    return_date: date | None = None


class ReservationStatus(str):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class BookReservationCreate(BaseModel):
    book_id: UUID
    student_id: UUID
    reservation_date: date | None = None


class BookReservationUpdate(BaseModel):
    status: str | None = None
    approval_date: date | None = None


class BookReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    book_id: UUID
    student_id: UUID
    reservation_date: date
    status: str
    approval_date: date | None
    created_at: datetime
    updated_at: datetime
    book_title: str | None = None
    book_author: str | None = None
    student_name: str | None = None
    student_class: str | None = None


class LibrarySettingsCreate(BaseModel):
    max_books_per_student: int = Field(..., gt=0)
    fine_per_day: Decimal = Field(..., ge=0)
    reservation_limit: int = Field(..., ge=0)
    borrow_duration: int = Field(..., gt=0)


class LibrarySettingsUpdate(BaseModel):
    max_books_per_student: int | None = None
    fine_per_day: Decimal | None = None
    reservation_limit: int | None = None
    borrow_duration: int | None = None


class LibrarySettingsResponse(LibrarySettingsCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class FinePaymentCreate(BaseModel):
    issue_id: UUID | None = None
    amount: Decimal = Field(..., ge=0)
    status: str | None = None


class FinePaymentUpdate(BaseModel):
    amount: Decimal | None = None
    status: str | None = None


class FinePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    issue_id: UUID
    amount: Decimal
    payment_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    book_title: str | None = None
    student_name: str | None = None
