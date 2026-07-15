from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave_model import LeaveRequest, LeaveStatus, LeaveType


class LeaveTypeRepository:
    async def create(self, session: AsyncSession, data: dict):
        item = LeaveType(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: UUID):
        return await session.get(LeaveType, item_id)

    async def get_by_name(self, session: AsyncSession, leave_type_name: str):
        result = await session.execute(
            select(LeaveType).where(LeaveType.leave_type_name == leave_type_name)
        )
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(LeaveType))
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, item: LeaveType, data: dict):
        for field, value in data.items():
            setattr(item, field, value)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def delete(self, session: AsyncSession, item: LeaveType) -> None:
        await session.delete(item)
        await session.flush()


class LeaveRequestRepository:
    async def create(self, session: AsyncSession, data: dict):
        item = LeaveRequest(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: UUID):
        return await session.get(LeaveRequest, item_id)

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(LeaveRequest))
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, item: LeaveRequest, data: dict):
        for field, value in data.items():
            setattr(item, field, value)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def delete(self, session: AsyncSession, item: LeaveRequest) -> None:
        await session.delete(item)
        await session.flush()

    async def get_by_user(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(
            select(LeaveRequest).where(LeaveRequest.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_pending(self, session: AsyncSession):
        result = await session.execute(
            select(LeaveRequest).where(LeaveRequest.status == LeaveStatus.PENDING)
        )
        return list(result.scalars().all())


leave_type_repository = LeaveTypeRepository()
leave_request_repository = LeaveRequestRepository()
