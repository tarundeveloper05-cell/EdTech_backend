from app.api.v1.router_factory import build_crud_router
from app.schemas.timetable_schema import (
    TimetableCreate,
    TimetableResponse,
    TimetableUpdate,
)
from app.services.timetable_service import timetable_service

router = build_crud_router(
    timetable_service, TimetableCreate, TimetableUpdate, TimetableResponse
)
