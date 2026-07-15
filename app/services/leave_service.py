from collections import Counter
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave_model import LeaveStatus
from app.models.user import User
from app.repositories.leave_repository import (
    leave_request_repository,
    leave_type_repository,
)


class LeaveTypeService:
    async def create_leave_type(self, session: AsyncSession, data: dict):
        await self._validate_leave_type(session, data["leave_type_name"])
        item = await leave_type_repository.create(session, data)
        await session.commit()
        return item

    async def update_leave_type(self, session: AsyncSession, leave_type_id: UUID, data: dict):
        item = await self.get_leave_type(session, leave_type_id)
        if "leave_type_name" in data:
            await self._validate_leave_type(
                session, data["leave_type_name"], exclude_id=leave_type_id
            )
        item = await leave_type_repository.update(session, item, data)
        await session.commit()
        return item

    async def delete_leave_type(self, session: AsyncSession, leave_type_id: UUID):
        item = await self.get_leave_type(session, leave_type_id)
        await leave_type_repository.delete(session, item)
        await session.commit()

    async def get_leave_types(self, session: AsyncSession):
        return await leave_type_repository.get_all(session)

    async def get_leave_type(self, session: AsyncSession, leave_type_id: UUID):
        item = await leave_type_repository.get_by_id(session, leave_type_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave type not found",
            )
        return item

    async def _validate_leave_type(
        self,
        session: AsyncSession,
        leave_type_name: str,
        exclude_id: UUID | None = None,
    ) -> None:
        if not leave_type_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave type name cannot be empty",
            )
        existing = await leave_type_repository.get_by_name(session, leave_type_name)
        if existing is not None and existing.id != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave type name must be unique",
            )


class LeaveRequestService:
    async def apply_leave(self, session: AsyncSession, data: dict):
        await self._validate_leave_request(session, data)
        data["status"] = LeaveStatus.PENDING
        item = await leave_request_repository.create(session, data)
        await session.commit()
        return item

    async def update_leave(self, session: AsyncSession, leave_id: UUID, data: dict):
        item = await self.get_leave(session, leave_id)
        if item.status != LeaveStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending leave requests can be updated",
            )
        merged = {
            "user_id": item.user_id,
            "leave_type_id": item.leave_type_id,
            "from_date": item.from_date,
            "to_date": item.to_date,
            "reason": item.reason,
        }
        merged.update(data)
        await self._validate_leave_request(session, merged)
        item = await leave_request_repository.update(session, item, data)
        await session.commit()
        return item

    async def cancel_leave(self, session: AsyncSession, leave_id: UUID):
        item = await self.get_leave(session, leave_id)
        if item.status not in (LeaveStatus.PENDING, LeaveStatus.APPROVED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending or approved leave requests can be cancelled",
            )
        item = await leave_request_repository.update(
            session, item, {"status": LeaveStatus.CANCELLED}
        )
        await session.commit()
        return item

    async def approve_leave(
        self, session: AsyncSession, leave_id: UUID, current_admin_user: User
    ):
        self._ensure_admin(current_admin_user)
        item = await self.get_leave(session, leave_id)
        item = await leave_request_repository.update(
            session,
            item,
            {"status": LeaveStatus.APPROVED, "approved_by": current_admin_user.id},
        )
        await session.commit()
        return item

    async def reject_leave(
        self, session: AsyncSession, leave_id: UUID, current_admin_user: User
    ):
        self._ensure_admin(current_admin_user)
        item = await self.get_leave(session, leave_id)
        item = await leave_request_repository.update(
            session,
            item,
            {"status": LeaveStatus.REJECTED, "approved_by": current_admin_user.id},
        )
        await session.commit()
        return item

    async def get_leave(self, session: AsyncSession, leave_id: UUID):
        item = await leave_request_repository.get_by_id(session, leave_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found",
            )
        return item

    async def get_leaves(self, session: AsyncSession):
        return await leave_request_repository.get_all(session)

    async def get_user_leaves(self, session: AsyncSession, user_id: UUID):
        if await session.get(User, user_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return await leave_request_repository.get_by_user(session, user_id)

    async def get_pending(self, session: AsyncSession):
        return await leave_request_repository.get_pending(session)

    async def delete_leave(self, session: AsyncSession, leave_id: UUID):
        item = await self.get_leave(session, leave_id)
        await leave_request_repository.delete(session, item)
        await session.commit()

    async def get_summary(self, session: AsyncSession) -> dict:
        leaves = await self.get_leaves(session)
        counts = Counter(
            leave.status.value if hasattr(leave.status, "value") else leave.status
            for leave in leaves
        )
        return {
            "total_requests": len(leaves),
            "pending": counts["PENDING"],
            "approved": counts["APPROVED"],
            "rejected": counts["REJECTED"],
            "cancelled": counts["CANCELLED"],
        }

    async def _validate_leave_request(self, session: AsyncSession, data: dict) -> None:
        if await session.get(User, data["user_id"]) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must exist",
            )
        if await leave_type_repository.get_by_id(session, data["leave_type_id"]) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave type must exist",
            )
        if data["from_date"] > data["to_date"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="from_date cannot be after to_date",
            )
        if not data["reason"].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reason cannot be empty",
            )
        if (data["to_date"] - data["from_date"]).days + 1 <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave duration must be greater than zero",
            )

    def _ensure_admin(self, current_user: User) -> None:
        role_name = current_user.role.role_name if current_user.role is not None else None
        if role_name != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can approve or reject leave requests",
            )


leave_type_service = LeaveTypeService()
leave_request_service = LeaveRequestService()
