from app.api.v1.router_factory import build_crud_router
from app.schemas.parent_schema import ParentCreate, ParentResponse, ParentUpdate
from app.services.parent_service import parent_service

router = build_crud_router(parent_service, ParentCreate, ParentUpdate, ParentResponse)
