from app.api.v1.router_factory import build_crud_router
from app.schemas.exam_schema import (
    ExamResultCreate,
    ExamResultResponse,
    ExamResultUpdate,
)
from app.services.exam_result_service import exam_result_service

router = build_crud_router(
    exam_result_service,
    ExamResultCreate,
    ExamResultUpdate,
    ExamResultResponse,
)
