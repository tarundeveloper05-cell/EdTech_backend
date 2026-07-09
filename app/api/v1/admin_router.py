from app.api.v1.router_factory import build_crud_router
from app.schemas.admin_schema import AdminCreate, AdminResponse, AdminUpdate
from app.services.admin_service import admin_service

router = build_crud_router(admin_service, AdminCreate, AdminUpdate, AdminResponse)
