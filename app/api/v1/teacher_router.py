from app.api.v1.router_factory import build_crud_router
from app.schemas.teacher_schema import TeacherCreate, TeacherResponse, TeacherUpdate
from app.services.teacher_service import teacher_service

router = build_crud_router(teacher_service, TeacherCreate, TeacherUpdate, TeacherResponse)
