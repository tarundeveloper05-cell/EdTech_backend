from app.repositories.admin_repository import admin_repository
from app.services.crud_service import CRUDService, USER_FK

admin_service = CRUDService(
    admin_repository, "Admin", ("user_id",), foreign_keys=USER_FK
)
