from app.repositories.parent_student_repository import parent_student_repository
from app.services.crud_service import CRUDService, PARENT_STUDENT_FKS

parent_student_service = CRUDService(
    parent_student_repository, "ParentStudent", (), PARENT_STUDENT_FKS
)
