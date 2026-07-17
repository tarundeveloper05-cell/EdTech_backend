from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.library_model import Book, BookIssue, BookIssueStatus
from app.schemas.library_schema import BookCategoryCreate, BookCategoryResponse, BookCategoryUpdate, BookCreate, BookIssueCreate, BookIssueResponse, BookIssueUpdate, BookResponse, BookReturnRequest, BookUpdate
from app.services.library_service import book_category_service, book_issue_service, book_service

book_category_router = APIRouter()
@book_category_router.post("", response_model=BookCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(payload: BookCategoryCreate, session: AsyncSession = Depends(get_db)): return await book_category_service.create_category(session, payload.model_dump())
@book_category_router.get("", response_model=list[BookCategoryResponse])
async def get_categories(session: AsyncSession = Depends(get_db)): return await book_category_service.get_categories(session)
@book_category_router.get("/{item_id}", response_model=BookCategoryResponse)
async def get_category(item_id: UUID, session: AsyncSession = Depends(get_db)): return await book_category_service.get_category(session, item_id)
@book_category_router.put("/{item_id}", response_model=BookCategoryResponse)
async def update_category(item_id: UUID, payload: BookCategoryUpdate, session: AsyncSession = Depends(get_db)): return await book_category_service.update_category(session, item_id, payload.model_dump(exclude_unset=True))
@book_category_router.delete("/{item_id}")
async def delete_category(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await book_category_service.delete_category(session, item_id)
    return {"message": "Deleted successfully"}
@book_category_router.get("/{category_id}/books", response_model=list[BookResponse])
async def get_category_books(category_id: UUID, session: AsyncSession = Depends(get_db)): return await book_service.get_books_by_category(session, category_id)

book_router = APIRouter()
@book_router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, session: AsyncSession = Depends(get_db)): return await book_service.create_book(session, payload.model_dump())
@book_router.get("", response_model=list[BookResponse])
async def get_books(session: AsyncSession = Depends(get_db)): return await book_service.get_books(session)
@book_router.get("/{item_id}", response_model=BookResponse)
async def get_book(item_id: UUID, session: AsyncSession = Depends(get_db)): return await book_service.get_book(session, item_id)
@book_router.put("/{item_id}", response_model=BookResponse)
async def update_book(item_id: UUID, payload: BookUpdate, session: AsyncSession = Depends(get_db)): return await book_service.update_book(session, item_id, payload.model_dump(exclude_unset=True))
@book_router.delete("/{item_id}")
async def delete_book(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await book_service.delete_book(session, item_id)
    return {"message": "Deleted successfully"}
@book_router.post("/{book_id}/issue", response_model=BookIssueResponse, status_code=status.HTTP_201_CREATED)
async def issue_book(book_id: UUID, payload: BookIssueCreate, session: AsyncSession = Depends(get_db)): return await book_issue_service.issue_book(session, book_id, payload.model_dump())

book_issue_router = APIRouter()
@book_issue_router.post("", response_model=BookIssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(payload: BookIssueCreate, session: AsyncSession = Depends(get_db)): return await book_issue_service.create_issue(session, payload.model_dump())
@book_issue_router.get("", response_model=list[BookIssueResponse])
async def get_issues(session: AsyncSession = Depends(get_db)): return await book_issue_service.get_issues(session)
@book_issue_router.get("/overdue", response_model=list[BookIssueResponse])
async def get_overdue_issues(session: AsyncSession = Depends(get_db)): return await book_issue_service.get_overdue(session)
@book_issue_router.get("/{item_id}", response_model=BookIssueResponse)
async def get_issue(item_id: UUID, session: AsyncSession = Depends(get_db)): return await book_issue_service.get_issue(session, item_id)
@book_issue_router.put("/{item_id}", response_model=BookIssueResponse)
async def update_issue(item_id: UUID, payload: BookIssueUpdate, session: AsyncSession = Depends(get_db)): return await book_issue_service.update_issue(session, item_id, payload.model_dump(exclude_unset=True))
@book_issue_router.delete("/{item_id}")
async def delete_issue(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await book_issue_service.delete_issue(session, item_id)
    return {"message": "Deleted successfully"}
@book_issue_router.patch("/{issue_id}/return", response_model=BookIssueResponse)
async def return_book(issue_id: UUID, payload: BookReturnRequest, session: AsyncSession = Depends(get_db)): return await book_issue_service.return_book(session, issue_id, payload.return_date)

student_library_router = APIRouter()
@student_library_router.get("/{student_id}/book-issues", response_model=list[BookIssueResponse])
async def get_student_issues(student_id: UUID, session: AsyncSession = Depends(get_db)): return await book_issue_service.get_by_student(session, student_id)

library_router = APIRouter()
@library_router.get("/summary")
async def library_summary(session: AsyncSession = Depends(get_db)):
    await book_issue_service.refresh_overdue(session)
    total_books = await session.scalar(select(func.coalesce(func.sum(Book.total_copies), 0)))
    available_books = await session.scalar(select(func.coalesce(func.sum(Book.available_copies), 0)))
    overdue_books = await session.scalar(select(func.count(BookIssue.id)).where(BookIssue.status == BookIssueStatus.OVERDUE.value))
    return {"total_books": total_books, "available_books": available_books, "issued_books": total_books - available_books, "overdue_books": overdue_books}
