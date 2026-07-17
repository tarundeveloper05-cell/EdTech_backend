from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event_model import AcademicCalendar, Event
from app.repositories.crud_repository import CRUDRepository


class EventRepository(CRUDRepository[Event]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID):
        return await self.get(session, item_id)

    async def get_all(self, session: AsyncSession):
        return await self.list(session)

    async def get_by_creator(self, session: AsyncSession, creator_id: UUID):
        result = await session.execute(select(Event).where(Event.created_by == creator_id))
        return list(result.scalars().all())

    async def get_by_type(self, session: AsyncSession, event_type: str):
        result = await session.execute(select(Event).where(Event.event_type == event_type))
        return list(result.scalars().all())

    async def get_by_date_range(self, session: AsyncSession, start_date: date, end_date: date):
        result = await session.execute(
            select(Event).where(Event.start_date <= end_date, Event.end_date >= start_date).order_by(Event.start_date)
        )
        return list(result.scalars().all())

    async def get_upcoming(self, session: AsyncSession, today: date):
        result = await session.execute(select(Event).where(Event.start_date >= today).order_by(Event.start_date))
        return list(result.scalars().all())


class AcademicCalendarRepository(CRUDRepository[AcademicCalendar]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID):
        return await self.get(session, item_id)

    async def get_all(self, session: AsyncSession):
        return await self.list(session)

    async def get_by_month(self, session: AsyncSession, start_date: date, end_date: date):
        result = await session.execute(
            select(AcademicCalendar).where(AcademicCalendar.start_date <= end_date, AcademicCalendar.end_date >= start_date).order_by(AcademicCalendar.start_date)
        )
        return list(result.scalars().all())

    async def get_holidays(self, session: AsyncSession):
        result = await session.execute(select(AcademicCalendar).where(AcademicCalendar.is_holiday.is_(True)).order_by(AcademicCalendar.start_date))
        return list(result.scalars().all())


event_repository = EventRepository(Event)
academic_calendar_repository = AcademicCalendarRepository(AcademicCalendar)
