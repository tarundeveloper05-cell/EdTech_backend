from app.api.v1.router_factory import build_crud_router
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import department_service

router = build_crud_router(
    department_service, DepartmentCreate, DepartmentUpdate, DepartmentResponse
)
