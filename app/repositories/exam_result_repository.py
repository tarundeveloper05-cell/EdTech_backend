from app.models.exam_result_model import ExamResult
from app.repositories.crud_repository import CRUDRepository

exam_result_repository = CRUDRepository(ExamResult)
