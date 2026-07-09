from app.api.v1.router_factory import build_crud_router
from app.schemas.parent_student_schema import (
    ParentStudentCreate,
    ParentStudentResponse,
    ParentStudentUpdate,
)
from app.services.parent_student_service import parent_student_service

router = build_crud_router(
    parent_student_service,
    ParentStudentCreate,
    ParentStudentUpdate,
    ParentStudentResponse,
)
