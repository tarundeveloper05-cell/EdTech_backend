from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.library_model import BookIssueStatus
from app.models.student_model import Student
from app.repositories.library_repository import book_category_repository, book_issue_repository, book_repository
from app.services.crud_service import CRUDService

FINE_RATE = Decimal("10.00")


def _bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class BookCategoryService(CRUDService):
    async def create_category(self, session: AsyncSession, data: dict):
        self._validate_name(data)
        return await self.create(session, data)
    async def update_category(self, session: AsyncSession, item_id: UUID, data: dict):
        self._validate_name(data)
        return await self.update(session, item_id, data)
    async def delete_category(self, session: AsyncSession, item_id: UUID): return await self.delete(session, item_id)
    async def get_category(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_categories(self, session: AsyncSession): return await self.list(session)
    def _validate_name(self, data: dict):
        if "category_name" in data and not data["category_name"].strip(): _bad_request("Category name cannot be empty")


class BookService(CRUDService):
    async def create_book(self, session: AsyncSession, data: dict):
        await self._validate_book(session, data)
        return await self.create(session, data)
    async def update_book(self, session: AsyncSession, item_id: UUID, data: dict):
        existing = await self.get(session, item_id)
        await self._validate_book(session, data, existing)
        return await self.update(session, item_id, data)
    async def delete_book(self, session: AsyncSession, item_id: UUID): return await self.delete(session, item_id)
    async def get_book(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_books(self, session: AsyncSession): return await self.list(session)
    async def get_books_by_category(self, session: AsyncSession, category_id: UUID):
        await book_category_service.get_category(session, category_id)
        return await self.repository.get_by_category(session, category_id)

    async def _validate_book(self, session: AsyncSession, data: dict, existing=None):
        for field, label in (("isbn", "ISBN"), ("title", "Title"), ("author", "Author")):
            if field in data and not data[field].strip(): _bad_request(f"{label} cannot be empty")
        if "category_id" in data and await book_category_repository.get(session, data["category_id"]) is None:
            _bad_request("Book category must exist")
        total = data.get("total_copies", getattr(existing, "total_copies", None))
        available = data.get("available_copies", getattr(existing, "available_copies", None))
        if total is not None and total <= 0: _bad_request("Total copies must be greater than zero")
        if available is not None and available < 0: _bad_request("Available copies cannot be negative")
        if total is not None and available is not None and available > total: _bad_request("Available copies cannot exceed total copies")


class BookIssueService(CRUDService):
    async def create_issue(self, session: AsyncSession, data: dict):
        return await self._issue(session, data)

    async def issue_book(self, session: AsyncSession, book_id: UUID, data: dict):
        if data["book_id"] != book_id: _bad_request("Book ID must match the requested book")
        return await self._issue(session, data)

    async def _issue(self, session: AsyncSession, data: dict):
        book = await book_service.get_book(session, data["book_id"])
        if await session.get(Student, data["student_id"]) is None: _bad_request("Student must exist")
        if book.available_copies <= 0: _bad_request("No copies are available for issue")
        if data["due_date"] <= data["issue_date"]: _bad_request("Due date must be after issue date")
        if await self.repository.get_active_issue(session, data["book_id"], data["student_id"]): _bad_request("Student already has an active issue for this book")
        issue = await self.repository.create(session, {**data, "fine_amount": Decimal("0.00"), "status": BookIssueStatus.ISSUED.value})
        book.available_copies -= 1
        session.add(book)
        await session.commit()
        await session.refresh(issue)
        return issue

    async def update_issue(self, session: AsyncSession, item_id: UUID, data: dict):
        issue = await self.get(session, item_id)
        issue_date = data.get("issue_date", issue.issue_date)
        due_date = data.get("due_date", issue.due_date)
        if due_date <= issue_date: _bad_request("Due date must be after issue date")
        return await self.update(session, item_id, data)

    async def return_book(self, session: AsyncSession, item_id: UUID, return_date: date | None):
        issue = await self.get(session, item_id)
        if issue.status == BookIssueStatus.RETURNED.value: _bad_request("Book issue has already been returned")
        returned_on = return_date or date.today()
        if returned_on < issue.issue_date: _bad_request("Return date cannot be before issue date")
        book = await book_service.get_book(session, issue.book_id)
        issue.return_date = returned_on
        issue.status = BookIssueStatus.RETURNED.value
        issue.fine_amount = self._fine(issue.due_date, returned_on)
        book.available_copies += 1
        session.add_all([issue, book])
        await session.commit()
        await session.refresh(issue)
        return issue

    async def refresh_overdue(self, session: AsyncSession):
        issues = await self.repository.get_overdue(session)
        changed = False
        for issue in issues:
            amount = self._fine(issue.due_date, date.today())
            if issue.status != BookIssueStatus.OVERDUE.value or issue.fine_amount != amount:
                issue.status, issue.fine_amount, changed = BookIssueStatus.OVERDUE.value, amount, True
        if changed: await session.commit()
        return issues

    async def get_issue(self, session: AsyncSession, item_id: UUID):
        await self.refresh_overdue(session)
        return await self.get(session, item_id)
    async def get_issues(self, session: AsyncSession):
        await self.refresh_overdue(session)
        return await self.list(session)
    async def get_by_student(self, session: AsyncSession, student_id: UUID):
        if await session.get(Student, student_id) is None: _bad_request("Student must exist")
        await self.refresh_overdue(session)
        return await self.repository.get_by_student(session, student_id)
    async def get_overdue(self, session: AsyncSession): return await self.refresh_overdue(session)
    async def delete_issue(self, session: AsyncSession, item_id: UUID):
        issue = await self.get(session, item_id)
        if issue.status != BookIssueStatus.RETURNED.value:
            book = await book_service.get_book(session, issue.book_id)
            book.available_copies += 1
            session.add(book)
        await self.repository.delete(session, issue)
        await session.commit()
    @staticmethod
    def _fine(due_date: date, comparison_date: date) -> Decimal:
        return Decimal(max(0, (comparison_date - due_date).days)) * FINE_RATE


book_category_service = BookCategoryService(book_category_repository, "Book category", ("category_name",))
book_service = BookService(book_repository, "Book", ("isbn",))
book_issue_service = BookIssueService(book_issue_repository, "Book issue")
