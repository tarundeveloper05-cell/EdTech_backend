from app.repositories.class_repository import class_repository
from app.services.crud_service import CLASS_FKS, CRUDService

class_service = CRUDService(
    class_repository,
    "Class",
    unique_constraints=(("class_name", "section", "academic_year"),),
    foreign_keys=CLASS_FKS,
)
