from app.models.timetable_model import Timetable
from app.repositories.crud_repository import CRUDRepository

timetable_repository = CRUDRepository(Timetable)
