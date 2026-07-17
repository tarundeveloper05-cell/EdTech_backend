from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusCreate(BaseModel):
    bus_number: str
    model: str
    capacity: int


class BusUpdate(BaseModel):
    bus_number: str | None = None
    model: str | None = None
    capacity: int | None = None


class BusResponse(BusCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class RouteCreate(BaseModel):
    route_name: str
    start_point: str
    end_point: str


class RouteUpdate(BaseModel):
    route_name: str | None = None
    start_point: str | None = None
    end_point: str | None = None


class RouteResponse(RouteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime


class StudentTransportCreate(BaseModel):
    student_id: UUID
    bus_id: UUID
    route_id: UUID
    stop_point: str


class StudentTransportUpdate(BaseModel):
    student_id: UUID | None = None
    bus_id: UUID | None = None
    route_id: UUID | None = None
    stop_point: str | None = None


class StudentTransportResponse(StudentTransportCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime
