from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.transport_model import Bus, Route, StudentTransport
from app.schemas.transport_schema import BusCreate, BusResponse, BusUpdate, RouteCreate, RouteResponse, RouteUpdate, StudentTransportCreate, StudentTransportResponse, StudentTransportUpdate
from app.services.transport_service import bus_service, route_service, student_transport_service

bus_router = APIRouter()
@bus_router.post("", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def create_bus(payload: BusCreate, session: AsyncSession = Depends(get_db)): return await bus_service.create_bus(session, payload.model_dump())
@bus_router.get("", response_model=list[BusResponse])
async def get_buses(session: AsyncSession = Depends(get_db)): return await bus_service.get_buses(session)
@bus_router.get("/{item_id}", response_model=BusResponse)
async def get_bus(item_id: UUID, session: AsyncSession = Depends(get_db)): return await bus_service.get_bus(session, item_id)
@bus_router.put("/{item_id}", response_model=BusResponse)
async def update_bus(item_id: UUID, payload: BusUpdate, session: AsyncSession = Depends(get_db)): return await bus_service.update_bus(session, item_id, payload.model_dump(exclude_unset=True))
@bus_router.delete("/{item_id}")
async def delete_bus(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await bus_service.delete_bus(session, item_id)
    return {"message": "Deleted successfully"}
@bus_router.get("/{bus_id}/students", response_model=list[StudentTransportResponse])
async def get_bus_students(bus_id: UUID, session: AsyncSession = Depends(get_db)): return await student_transport_service.get_by_bus(session, bus_id)
@bus_router.get("/{bus_id}/capacity")
async def get_bus_capacity(bus_id: UUID, session: AsyncSession = Depends(get_db)):
    bus = await bus_service.get_bus(session, bus_id)
    assigned_students = await student_transport_service.repository.count_by_bus(session, bus_id)
    return {"bus_id": str(bus.id), "capacity": bus.capacity, "assigned_students": assigned_students, "available_seats": bus.capacity - assigned_students}

route_router = APIRouter()
@route_router.post("", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(payload: RouteCreate, session: AsyncSession = Depends(get_db)): return await route_service.create_route(session, payload.model_dump())
@route_router.get("", response_model=list[RouteResponse])
async def get_routes(session: AsyncSession = Depends(get_db)): return await route_service.get_routes(session)
@route_router.get("/{item_id}", response_model=RouteResponse)
async def get_route(item_id: UUID, session: AsyncSession = Depends(get_db)): return await route_service.get_route(session, item_id)
@route_router.put("/{item_id}", response_model=RouteResponse)
async def update_route(item_id: UUID, payload: RouteUpdate, session: AsyncSession = Depends(get_db)): return await route_service.update_route(session, item_id, payload.model_dump(exclude_unset=True))
@route_router.delete("/{item_id}")
async def delete_route(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await route_service.delete_route(session, item_id)
    return {"message": "Deleted successfully"}
@route_router.get("/{route_id}/students", response_model=list[StudentTransportResponse])
async def get_route_students(route_id: UUID, session: AsyncSession = Depends(get_db)): return await student_transport_service.get_by_route(session, route_id)

student_transport_router = APIRouter()
@student_transport_router.post("", response_model=StudentTransportResponse, status_code=status.HTTP_201_CREATED)
async def create_transport(payload: StudentTransportCreate, session: AsyncSession = Depends(get_db)): return await student_transport_service.create_transport(session, payload.model_dump())
@student_transport_router.get("", response_model=list[StudentTransportResponse])
async def get_transports(session: AsyncSession = Depends(get_db)): return await student_transport_service.get_transports(session)
@student_transport_router.get("/{item_id}", response_model=StudentTransportResponse)
async def get_transport(item_id: UUID, session: AsyncSession = Depends(get_db)): return await student_transport_service.get_transport(session, item_id)
@student_transport_router.put("/{item_id}", response_model=StudentTransportResponse)
async def update_transport(item_id: UUID, payload: StudentTransportUpdate, session: AsyncSession = Depends(get_db)): return await student_transport_service.update_transport(session, item_id, payload.model_dump(exclude_unset=True))
@student_transport_router.delete("/{item_id}")
async def delete_transport(item_id: UUID, session: AsyncSession = Depends(get_db)):
    await student_transport_service.delete_transport(session, item_id)
    return {"message": "Deleted successfully"}

student_transport_detail_router = APIRouter()
@student_transport_detail_router.get("/{student_id}/transport", response_model=StudentTransportResponse)
async def get_student_transport(student_id: UUID, session: AsyncSession = Depends(get_db)): return await student_transport_service.get_by_student(session, student_id)

transport_router = APIRouter()
@transport_router.get("/summary")
async def transport_summary(session: AsyncSession = Depends(get_db)):
    total_buses = await session.scalar(select(func.count(Bus.id)))
    total_routes = await session.scalar(select(func.count(Route.id)))
    students_using_transport = await session.scalar(select(func.count(StudentTransport.id)))
    total_capacity = await session.scalar(select(func.coalesce(func.sum(Bus.capacity), 0)))
    return {"total_buses": total_buses, "total_routes": total_routes, "students_using_transport": students_using_transport, "available_seats": total_capacity - students_using_transport}
