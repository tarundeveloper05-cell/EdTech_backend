from app.repositories.department_repository import department_repository
from app.services.crud_service import CRUDService

department_service = CRUDService(
    department_repository, "Department", ("department_name",)
)
