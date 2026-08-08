from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.routes import get_current_user
from app.api.v1.router_factory import require_roles
from app.api.v1.router_factory import build_crud_router
from app.core.database import get_db
from app.models.exam_result_model import ExamResult
from app.models.student_model import Student
from app.models.user import User
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentUpdate
from app.schemas.exam_schema import (
    ExamResultResponse,
    ReportCardResponse,
    StudentPerformanceSummary,
)
from app.services.report_card_service import report_card_service
from app.services.student_service import student_service

router = build_crud_router(student_service, StudentCreate, StudentUpdate, StudentResponse)


async def get_current_student(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Student:
    result = await session.execute(select(Student).where(Student.user_id == current_user.id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return student


@router.get("/me", response_model=StudentResponse)
async def get_current_student_profile(
    student: Student = Depends(get_current_student),
):
    return student


@router.get("/me/hostel", response_model=dict)
async def get_current_student_hostel(
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_db),
):
    from app.models.hostel_model import HostelAllocation, HostelAllocationStatus
    result = await session.execute(
        select(HostelAllocation)
        .where(HostelAllocation.student_id == student.id)
        .where(HostelAllocation.status == HostelAllocationStatus.ACTIVE)
        .limit(1)
    )
    allocation = result.scalar_one_or_none()
    if allocation is None:
        return {"allocated": False, "block_name": None, "room_no": None, "bed_no": None, "status": "NOT_ALLOCATED"}
    bed = allocation.bed
    room = bed.room if bed else None
    block = room.block if room else None
    return {
        "allocated": True,
        "block_name": block.block_name if block else None,
        "block_type": block.block_type if block else None,
        "room_no": room.room_no if room else None,
        "bed_no": bed.bed_no if bed else None,
        "floor_no": room.floor_no if room else None,
        "check_in_date": str(allocation.check_in_date),
        "status": allocation.status.value,
    }


@router.get("/me/hostel-fees", response_model=dict)
async def get_current_student_hostel_fees(
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_db),
):
    from app.models.hostel_operations_model import HostelFeeInvoice, HostelInvoiceStatus
    result = await session.execute(
        select(HostelFeeInvoice).where(HostelFeeInvoice.student_id == student.id)
    )
    invoices = result.scalars().all()
    total = sum(float(inv.amount) for inv in invoices)
    paid = sum(float(inv.amount) for inv in invoices if inv.status == HostelInvoiceStatus.PAID)
    pending = total - paid
    return {
        "total_fees": total,
        "paid_amount": paid,
        "pending_amount": pending,
        "invoices": [
            {
                "id": str(inv.id),
                "fee_type": inv.fee_structure.fee_type if inv.fee_structure else "Hostel Fee",
                "amount": float(inv.amount),
                "status": inv.status.value,
                "invoice_date": str(inv.invoice_date),
                "due_date": str(inv.due_date),
            }
            for inv in invoices
        ],
    }


@router.get("/me/attendance", response_model=dict)
async def get_current_student_attendance(
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_db),
):
    from app.models.attendance_model import Attendance
    result = await session.execute(
        select(Attendance).where(Attendance.student_id == student.id)
    )
    records = result.scalars().all()
    total = len(records)
    present = sum(1 for r in records if r.status == "PRESENT")
    absent = sum(1 for r in records if r.status == "ABSENT")
    late = sum(1 for r in records if r.status == "LATE")
    percentage = (present / total * 100) if total > 0 else 0
    return {
        "total_classes": total,
        "present": present,
        "absent": absent,
        "late": late,
        "attendance_percentage": round(percentage, 2),
    }


@router.get("/me/fees", response_model=dict)
async def get_current_student_fees(
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_db),
):
    from app.services.fee_service import fee_invoice_service, payment_service

    summary = await fee_invoice_service.get_student_fee_summary(session, student.id)
    invoices = await fee_invoice_service.get_by_student(session, student.id)
    outstanding_invoices = await fee_invoice_service.get_outstanding_by_student(session, student.id)
    payments = await payment_service.get_by_student(session, student.id)

    return {
        "total_fees": summary["total_fees"],
        "paid_amount": summary["paid"],
        "pending_amount": summary["pending"],
        "outstanding_invoices": len(outstanding_invoices),
        "invoices": [
            {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number or f"INV-{inv.id}",
                "amount": float(inv.net_amount if inv.net_amount else inv.amount),
                "paid_amount": sum(float(p.amount_paid) for p in inv.payments),
                "pending_amount": float(inv.net_amount if inv.net_amount else inv.amount) - sum(float(p.amount_paid) for p in inv.payments),
                "status": inv.status,
                "due_date": str(inv.due_date) if inv.due_date else None,
                "invoice_date": str(inv.invoice_date) if inv.invoice_date else None,
            }
            for inv in invoices
        ],
        "payment_history": [
            {
                "payment_id": str(p.id),
                "date": str(p.payment_date) if p.payment_date else None,
                "amount": float(p.amount_paid),
                "method": p.payment_method,
                "receipt": p.receipt_number or p.receipt_no or "",
                "status": p.payment_status,
            }
            for p in payments
        ],
    }


@router.get("/me/library", response_model=dict)
async def get_current_student_library(
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_db),
):
    from app.models.library_model import BookIssue, BookReservation, FinePayment, BookIssueStatus, ReservationStatus, FinePaymentStatus
    issues_result = await session.execute(
        select(BookIssue).where(BookIssue.student_id == student.id)
    )
    issues = issues_result.scalars().all()
    reservations_result = await session.execute(
        select(BookReservation).where(BookReservation.student_id == student.id)
    )
    reservations = reservations_result.scalars().all()
    fines_result = await session.execute(
        select(FinePayment).join(BookIssue).where(BookIssue.student_id == student.id)
    )
    fines = fines_result.scalars().all()
    active_issues = [i for i in issues if i.status == BookIssueStatus.ISSUED.value]
    overdue_issues = [i for i in issues if i.status == BookIssueStatus.OVERDUE.value]
    returned_issues = [i for i in issues if i.status == BookIssueStatus.RETURNED.value]
    return {
        "active_books": len(active_issues),
        "overdue_books": len(overdue_issues),
        "returned_books": len(returned_issues),
        "total_fine": sum(float(f.amount) for f in fines if f.status == FinePaymentStatus.PAID.value),
        "outstanding_fine": sum(float(f.amount) for f in fines if f.status != FinePaymentStatus.PAID.value),
        "active_issues": [
            {
                "id": str(i.id),
                "book_title": i.book_title,
                "book_author": i.book_author,
                "issue_date": str(i.issue_date),
                "due_date": str(i.due_date),
                "status": i.status,
                "fine_amount": float(i.fine_amount),
            }
            for i in active_issues
        ],
        "overdue_issues": [
            {
                "id": str(i.id),
                "book_title": i.book_title,
                "book_author": i.book_author,
                "issue_date": str(i.issue_date),
                "due_date": str(i.due_date),
                "status": i.status,
                "fine_amount": float(i.fine_amount),
            }
            for i in overdue_issues
        ],
        "reservations": [
            {
                "id": str(r.id),
                "book_title": r.book_title,
                "reservation_date": str(r.reservation_date),
                "status": r.status,
            }
            for r in reservations
        ],
    }


@router.get("/{student_id}/exam-results", response_model=list[ExamResultResponse])
async def get_student_exam_results(
    student_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ensure_student_access(session, current_user, student_id)
    result = await session.execute(
        select(ExamResult).where(ExamResult.student_id == student_id)
    )
    return result.scalars().all()


@router.get("/{student_id}/report-cards", response_model=list[ReportCardResponse])
async def get_student_report_cards(
    student_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ensure_student_access(session, current_user, student_id)
    return await report_card_service.get_student_report_cards(session, student_id)


@router.get("/{student_id}/performance", response_model=StudentPerformanceSummary)
async def get_student_performance(
    student_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await ensure_student_access(session, current_user, student_id)
    return await report_card_service.get_performance_summary(session, student_id)


async def ensure_student_access(
    session: AsyncSession,
    current_user: User,
    student_id: UUID,
) -> None:
    role_name = current_user.role.role_name.upper() if current_user.role else ""
    if role_name == "ADMIN":
        await student_service.get(session, student_id)
        return
    if role_name == "STUDENT":
        result = await session.execute(
            select(Student).where(Student.id == student_id, Student.user_id == current_user.id)
        )
        if result.scalar_one_or_none() is not None:
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this student's records",
    )
