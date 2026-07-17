from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.library_model import Book, BookCategory, BookIssue, BookIssueStatus
from app.repositories.crud_repository import CRUDRepository


class BookCategoryRepository(CRUDRepository[BookCategory]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_by_name(self, session: AsyncSession, name: str):
        return (await session.execute(select(BookCategory).where(BookCategory.category_name == name))).scalar_one_or_none()
    async def get_all(self, session: AsyncSession): return await self.list(session)


class BookRepository(CRUDRepository[Book]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_by_isbn(self, session: AsyncSession, isbn: str):
        return (await session.execute(select(Book).where(Book.isbn == isbn))).scalar_one_or_none()
    async def get_all(self, session: AsyncSession): return await self.list(session)
    async def get_by_category(self, session: AsyncSession, category_id: UUID):
        return list((await session.execute(select(Book).where(Book.category_id == category_id))).scalars().all())


class BookIssueRepository(CRUDRepository[BookIssue]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_all(self, session: AsyncSession): return await self.list(session)
    async def get_by_student(self, session: AsyncSession, student_id: UUID):
        return list((await session.execute(select(BookIssue).where(BookIssue.student_id == student_id).order_by(BookIssue.issue_date.desc()))).scalars().all())
    async def get_by_book(self, session: AsyncSession, book_id: UUID):
        return list((await session.execute(select(BookIssue).where(BookIssue.book_id == book_id).order_by(BookIssue.issue_date.desc()))).scalars().all())
    async def get_active_issue(self, session: AsyncSession, book_id: UUID, student_id: UUID):
        query = select(BookIssue).where(BookIssue.book_id == book_id, BookIssue.student_id == student_id, BookIssue.status.in_([BookIssueStatus.ISSUED.value, BookIssueStatus.OVERDUE.value]))
        return (await session.execute(query)).scalar_one_or_none()
    async def get_overdue(self, session: AsyncSession):
        query = select(BookIssue).where(BookIssue.status != BookIssueStatus.RETURNED.value, BookIssue.due_date < date.today()).order_by(BookIssue.due_date)
        return list((await session.execute(query)).scalars().all())


book_category_repository = BookCategoryRepository(BookCategory)
book_repository = BookRepository(Book)
book_issue_repository = BookIssueRepository(BookIssue)
