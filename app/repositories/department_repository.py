from app.models.department_model import Department
from app.repositories.crud_repository import CRUDRepository

department_repository = CRUDRepository(Department)
