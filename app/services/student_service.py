from app.repositories.student_repository import student_repository
from app.services.crud_service import CRUDService, USER_FK

student_service = CRUDService(
    student_repository, "Student", ("user_id", "admission_no"), USER_FK
)
