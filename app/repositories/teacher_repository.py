from app.models.teacher_model import Teacher
from app.repositories.crud_repository import CRUDRepository

teacher_repository = CRUDRepository(Teacher)
