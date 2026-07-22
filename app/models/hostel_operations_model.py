import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class HostelInvoiceStatus(str, enum.Enum): PENDING="PENDING"; PAID="PAID"; OVERDUE="OVERDUE"
class MessAttendanceStatus(str, enum.Enum): PRESENT="PRESENT"; ABSENT="ABSENT"
class MaintenancePriority(str, enum.Enum): LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"; URGENT="URGENT"
class MaintenanceStatus(str, enum.Enum): OPEN="OPEN"; IN_PROGRESS="IN_PROGRESS"; RESOLVED="RESOLVED"; CLOSED="CLOSED"
class WorkOrderStatus(str, enum.Enum): OPEN="OPEN"; IN_PROGRESS="IN_PROGRESS"; COMPLETED="COMPLETED"

class HostelVisitor(Base):
    __tablename__="hostel_visitors"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    student_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("students.id"),nullable=False)
    visitor_name: Mapped[str]=mapped_column(String(255),nullable=False)
    relation: Mapped[str | None]=mapped_column(String(100),nullable=True)
    phone: Mapped[str]=mapped_column(String(30),nullable=False)
    check_in_time: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    check_out_time: Mapped[datetime | None]=mapped_column(DateTime(timezone=True),nullable=True)
    approved_by: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    student=relationship("Student",back_populates="hostel_visitors",lazy="selectin")
    approver=relationship("User",back_populates="approved_hostel_visitors",foreign_keys=[approved_by],lazy="selectin")

class HostelFeeStructure(Base):
    __tablename__="hostel_fee_structures"; __table_args__=(UniqueConstraint("fee_type","academic_year",name="uq_hostel_fee_type_year"),)
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    fee_type: Mapped[str]=mapped_column(String(100),nullable=False); amount: Mapped[Decimal]=mapped_column(Numeric(10,2),nullable=False)
    academic_year: Mapped[str]=mapped_column(String(50),nullable=False); description: Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    invoices=relationship("HostelFeeInvoice",back_populates="fee_structure")

class HostelFeeInvoice(Base):
    __tablename__="hostel_fee_invoices"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    student_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("students.id"),nullable=False); hostel_fee_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("hostel_fee_structures.id"),nullable=False)
    invoice_date: Mapped[date]=mapped_column(Date,nullable=False); due_date: Mapped[date]=mapped_column(Date,nullable=False); amount: Mapped[Decimal]=mapped_column(Numeric(10,2),nullable=False)
    status: Mapped[HostelInvoiceStatus]=mapped_column(String(20),nullable=False,default=HostelInvoiceStatus.PENDING,server_default="PENDING")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    student=relationship("Student",back_populates="hostel_fee_invoices",lazy="selectin"); fee_structure=relationship("HostelFeeStructure",back_populates="invoices",lazy="selectin"); payments=relationship("HostelPayment",back_populates="invoice")

class HostelPayment(Base):
    __tablename__="hostel_payments"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); invoice_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("hostel_fee_invoices.id"),nullable=False)
    payment_date: Mapped[date]=mapped_column(Date,nullable=False); amount_paid: Mapped[Decimal]=mapped_column(Numeric(10,2),nullable=False); payment_method: Mapped[str]=mapped_column(String(30),nullable=False)
    transaction_no: Mapped[str|None]=mapped_column(String(100),nullable=True); receipt_no: Mapped[str|None]=mapped_column(String(100),nullable=True); remarks: Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    invoice=relationship("HostelFeeInvoice",back_populates="payments",lazy="selectin")

class MessMenu(Base):
    __tablename__="mess_menu"; __table_args__=(UniqueConstraint("meal_type","menu_date",name="uq_mess_menu_meal_date"),)
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); meal_type: Mapped[str]=mapped_column(String(30),nullable=False); menu_date: Mapped[date]=mapped_column(Date,nullable=False)
    breakfast: Mapped[str|None]=mapped_column(Text,nullable=True); lunch: Mapped[str|None]=mapped_column(Text,nullable=True); dinner: Mapped[str|None]=mapped_column(Text,nullable=True); created_by: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class MessExpense(Base):
    __tablename__="mess_expenses"; id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); expense_date: Mapped[date]=mapped_column(Date,nullable=False); category: Mapped[str]=mapped_column(String(100),nullable=False); description: Mapped[str|None]=mapped_column(Text,nullable=True); amount: Mapped[Decimal]=mapped_column(Numeric(10,2),nullable=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
class MessCollection(Base):
    __tablename__="mess_collections"; id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); student_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("students.id"),nullable=False); amount: Mapped[Decimal]=mapped_column(Numeric(10,2),nullable=False); collection_date: Mapped[date]=mapped_column(Date,nullable=False); payment_method: Mapped[str]=mapped_column(String(30),nullable=False); received_by: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
class MessAttendance(Base):
    __tablename__="mess_attendance"; __table_args__=(UniqueConstraint("student_id","meal_type","attendance_date",name="uq_mess_attendance"),); id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); student_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("students.id"),nullable=False); meal_type: Mapped[str]=mapped_column(String(30),nullable=False); attendance_date: Mapped[date]=mapped_column(Date,nullable=False); status: Mapped[MessAttendanceStatus]=mapped_column(String(20),nullable=False); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class MaintenanceRequest(Base):
    __tablename__="maintenance_requests"; id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); requested_by: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("students.id"),nullable=False); room_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("hostel_rooms.id"),nullable=False); issue_type: Mapped[str]=mapped_column(String(100),nullable=False); description: Mapped[str]=mapped_column(Text,nullable=False); priority: Mapped[MaintenancePriority]=mapped_column(String(20),nullable=False,default=MaintenancePriority.MEDIUM); status: Mapped[MaintenanceStatus]=mapped_column(String(20),nullable=False,default=MaintenanceStatus.OPEN); requested_on: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now()); work_orders=relationship("WorkOrder",back_populates="request")
class WorkOrder(Base):
    __tablename__="work_orders"; id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); request_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("maintenance_requests.id"),nullable=False); assigned_to: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False); scheduled_date: Mapped[date]=mapped_column(Date,nullable=False); completed_date: Mapped[date|None]=mapped_column(Date,nullable=True); status: Mapped[WorkOrderStatus]=mapped_column(String(20),nullable=False,default=WorkOrderStatus.OPEN); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now()); request=relationship("MaintenanceRequest",back_populates="work_orders")
