from app.repositories.class_subject_repository import class_subject_repository
from app.services.crud_service import CLASS_SUBJECT_FKS, CRUDService

class_subject_service = CRUDService(
    class_subject_repository,
    "ClassSubject",
    unique_constraints=(("class_id", "subject_id"),),
    foreign_keys=CLASS_SUBJECT_FKS,
)
