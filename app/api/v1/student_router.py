from app.api.v1.router_factory import build_crud_router
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentUpdate
from app.services.student_service import student_service

router = build_crud_router(student_service, StudentCreate, StudentUpdate, StudentResponse)
