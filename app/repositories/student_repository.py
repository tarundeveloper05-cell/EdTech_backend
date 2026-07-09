from app.models.student_model import Student
from app.repositories.crud_repository import CRUDRepository

student_repository = CRUDRepository(Student)
