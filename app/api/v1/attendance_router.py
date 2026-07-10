from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
    BulkAttendanceCreate,
    ClassAttendanceSummary,
    StudentAttendanceReport,
    StudentAttendanceSummary,
    SubjectAttendanceSummary,
    TeacherAttendanceSummary,
)
from app.services.attendance_service import attendance_service

router = APIRouter()


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    payload: AttendanceCreate, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.create_attendance(session, payload.model_dump())


@router.post("/bulk", response_model=list[AttendanceResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_attendance(
    payload: BulkAttendanceCreate, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.create_bulk_attendance(session, payload.model_dump())


@router.get("", response_model=list[AttendanceResponse])
async def get_all_attendance(session: AsyncSession = Depends(get_db)):
    return await attendance_service.get_all_attendance(session)


@router.get("/student/{student_id}", response_model=list[AttendanceResponse])
async def get_attendance_by_student(
    student_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_student_attendance(session, student_id)


@router.get("/teacher/{teacher_id}", response_model=list[AttendanceResponse])
async def get_attendance_by_teacher(
    teacher_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_teacher_attendance(session, teacher_id)


@router.get("/class/{class_id}", response_model=list[AttendanceResponse])
async def get_attendance_by_class(
    class_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_class_attendance(session, class_id)


@router.get("/date/{attendance_date}", response_model=list[AttendanceResponse])
async def get_attendance_by_date(
    attendance_date: date, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_date_attendance(session, attendance_date)


@router.get("/student/{student_id}/report", response_model=StudentAttendanceReport)
async def get_student_report(
    student_id: UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    session: AsyncSession = Depends(get_db),
):
    records = await attendance_service.get_student_report(
        session, student_id, start_date, end_date
    )
    return {"student_id": student_id, "records": records}


@router.get("/student/{student_id}/summary", response_model=StudentAttendanceSummary)
async def get_student_summary(
    student_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_student_summary(session, student_id)


@router.get("/class/{class_id}/summary", response_model=ClassAttendanceSummary)
async def get_class_summary(class_id: UUID, session: AsyncSession = Depends(get_db)):
    return await attendance_service.get_class_summary(session, class_id)


@router.get("/subject/{subject_id}/summary", response_model=SubjectAttendanceSummary)
async def get_subject_summary(
    subject_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_subject_summary(session, subject_id)


@router.get("/teacher/{teacher_id}/summary", response_model=TeacherAttendanceSummary)
async def get_teacher_summary(
    teacher_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_teacher_summary(session, teacher_id)


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: UUID, session: AsyncSession = Depends(get_db)
):
    return await attendance_service.get_attendance(session, attendance_id)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: UUID,
    payload: AttendanceUpdate,
    session: AsyncSession = Depends(get_db),
):
    return await attendance_service.update_attendance(
        session, attendance_id, payload.model_dump()
    )


@router.delete("/{attendance_id}", status_code=status.HTTP_200_OK)
async def delete_attendance(
    attendance_id: UUID, session: AsyncSession = Depends(get_db)
):
    await attendance_service.delete_attendance(session, attendance_id)
    return {"message": "Deleted successfully"}
