from app.models.exam_model import Exam
from app.repositories.crud_repository import CRUDRepository

exam_repository = CRUDRepository(Exam)
