from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BookCategoryCreate(BaseModel):
    category_name: str
    description: str | None = None


class BookCategoryUpdate(BaseModel):
    category_name: str | None = None
    description: str | None = None


class BookCategoryResponse(BookCategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str | None = None
    category_id: UUID
    rack_no: str | None = None
    total_copies: int
    available_copies: int


class BookUpdate(BaseModel):
    isbn: str | None = None
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    category_id: UUID | None = None
    rack_no: str | None = None
    total_copies: int | None = None
    available_copies: int | None = None


class BookResponse(BookCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
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


class BookIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    book_id: UUID
    student_id: UUID
    issue_date: date
    due_date: date
    return_date: date | None
    fine_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime


class BookReturnRequest(BaseModel):
    return_date: date | None = None
