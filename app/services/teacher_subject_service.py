from app.repositories.teacher_subject_repository import teacher_subject_repository
from app.services.crud_service import CRUDService, TEACHER_SUBJECT_FKS

teacher_subject_service = CRUDService(
    teacher_subject_repository,
    "TeacherSubject",
    unique_constraints=(("teacher_id", "subject_id", "class_id"),),
    foreign_keys=TEACHER_SUBJECT_FKS,
)
