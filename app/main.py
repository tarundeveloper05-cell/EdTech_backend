from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin_router import router as admin_router
from app.api.v1.attendance_router import router as attendance_router
from app.api.v1.class_router import router as class_router
from app.api.v1.class_subject_router import router as class_subject_router
from app.api.v1.department_router import router as department_router
from app.api.v1.exam_result_router import router as exam_result_router
from app.api.v1.exam_router import router as exam_router
from app.api.v1.parent_router import router as parent_router
from app.api.v1.parent_student_router import router as parent_student_router
from app.api.v1.student_router import router as student_router
from app.api.v1.subject_router import router as subject_router
from app.api.v1.teacher_router import router as teacher_router
from app.api.v1.teacher_subject_router import router as teacher_subject_router
from app.api.v1.timetable_router import router as timetable_router
from app.api.v1.report_card_router import router as report_card_router
from app.api.v1.users.routes import router as user_router
from app.api.v1.assignment_router import router as assignment_router, submission_router, teacher_assignment_router, class_assignment_router, student_assignment_router
from app.api.v1.communication_router import announcement_router, notification_router, message_router, user_communication_router
from app.api.v1.fee_router import fee_structure_router, fee_invoice_router, payment_router, student_fee_router
from .api.v1.auth.routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Auth Service API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_router, prefix="/admins", tags=["Admins"])
app.include_router(department_router, prefix="/departments", tags=["Departments"])
app.include_router(teacher_router, prefix="/teachers", tags=["Teachers"])
app.include_router(parent_router, prefix="/parents", tags=["Parents"])
app.include_router(student_router, prefix="/students", tags=["Students"])
app.include_router(parent_student_router, prefix="/parent-students", tags=["Parent Students"])
app.include_router(class_router, prefix="/classes", tags=["Classes"])
app.include_router(subject_router, prefix="/subjects", tags=["Subjects"])
app.include_router(class_subject_router, prefix="/class-subjects", tags=["Class Subjects"])
app.include_router(teacher_subject_router, prefix="/teacher-subjects", tags=["Teacher Subjects"])
app.include_router(timetable_router, prefix="/timetables", tags=["Timetables"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(exam_router, prefix="/exams", tags=["Exams"])
app.include_router(exam_result_router, prefix="/exam-results", tags=["Exam Results"])
app.include_router(report_card_router, prefix="/report-cards", tags=["Report Cards"])
app.include_router(assignment_router, prefix="/assignments", tags=["Assignments"])
app.include_router(submission_router, prefix="/assignment-submissions", tags=["Assignment Submissions"])
app.include_router(teacher_assignment_router, prefix="/teachers", tags=["Teacher Assignments"])
app.include_router(class_assignment_router, prefix="/classes", tags=["Class Assignments"])
app.include_router(student_assignment_router, prefix="/students", tags=["Student Assignments"])
app.include_router(announcement_router, prefix="/announcements", tags=["Announcements"])
app.include_router(notification_router, prefix="/notifications", tags=["Notifications"])
app.include_router(message_router, prefix="/messages", tags=["Messages"])
app.include_router(user_communication_router, prefix="/users", tags=["User Communication"])
app.include_router(fee_structure_router, prefix="/fee-structures", tags=["Fee Structures"])
app.include_router(fee_invoice_router, prefix="/fee-invoices", tags=["Fee Invoices"])
app.include_router(payment_router, prefix="/payments", tags=["Payments"])
app.include_router(student_fee_router, prefix="/students", tags=["Student Fees"])
app.include_router(user_router, tags=["Users"])
app.include_router(auth_router, tags=["auth"])


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
