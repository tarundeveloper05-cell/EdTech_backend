from app.repositories.teacher_repository import teacher_repository
from app.services.crud_service import CRUDService, TEACHER_FKS

teacher_service = CRUDService(
    teacher_repository, "Teacher", ("user_id", "employee_id"), TEACHER_FKS
)
