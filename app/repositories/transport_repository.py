from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transport_model import Bus, Route, StudentTransport
from app.repositories.crud_repository import CRUDRepository


class BusRepository(CRUDRepository[Bus]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_by_bus_number(self, session: AsyncSession, bus_number: str):
        return (await session.execute(select(Bus).where(Bus.bus_number == bus_number))).scalar_one_or_none()
    async def get_all(self, session: AsyncSession): return await self.list(session)


class RouteRepository(CRUDRepository[Route]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_by_name(self, session: AsyncSession, route_name: str):
        return (await session.execute(select(Route).where(Route.route_name == route_name))).scalar_one_or_none()
    async def get_all(self, session: AsyncSession): return await self.list(session)


class StudentTransportRepository(CRUDRepository[StudentTransport]):
    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await self.get(session, item_id)
    async def get_all(self, session: AsyncSession): return await self.list(session)
    async def get_by_student(self, session: AsyncSession, student_id: UUID):
        return (await session.execute(select(StudentTransport).where(StudentTransport.student_id == student_id))).scalar_one_or_none()
    async def get_by_bus(self, session: AsyncSession, bus_id: UUID):
        return list((await session.execute(select(StudentTransport).where(StudentTransport.bus_id == bus_id))).scalars().all())
    async def get_by_route(self, session: AsyncSession, route_id: UUID):
        return list((await session.execute(select(StudentTransport).where(StudentTransport.route_id == route_id))).scalars().all())
    async def count_by_bus(self, session: AsyncSession, bus_id: UUID, exclude_id: UUID | None = None):
        query = select(func.count(StudentTransport.id)).where(StudentTransport.bus_id == bus_id)
        if exclude_id is not None: query = query.where(StudentTransport.id != exclude_id)
        return await session.scalar(query) or 0


bus_repository = BusRepository(Bus)
route_repository = RouteRepository(Route)
student_transport_repository = StudentTransportRepository(StudentTransport)
