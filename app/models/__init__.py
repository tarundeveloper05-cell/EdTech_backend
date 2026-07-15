from .permission import Permission
from .role import Role
from .role_permission import RolePermission
from .user import User
from .admin_model import Admin
from .department_model import Department
from .teacher_model import Teacher
from .parent_model import Parent
from .student_model import Student
from .parent_student_model import ParentStudent
from .class_model import Class
from .subject_model import Subject
from .class_subject_model import ClassSubject
from .teacher_subject_model import TeacherSubject
from .timetable_model import Timetable
from .attendance_model import Attendance, AttendanceStatus
from .exam_model import Exam
from .exam_result_model import ExamResult
from .report_card_model import ReportCard
from .assignment_model import Assignment, AssignmentSubmission
from .communication_model import Announcement, Notification, Message
from .fee_model import FeeStructure, FeeInvoice, Payment
from .admission_model import (
    AdmissionApplication,
    AdmissionApplicationStatus,
    AdmissionDocument,
)
from .leave_model import LeaveRequest, LeaveStatus, LeaveType

Faculty = Teacher
StudentParent = ParentStudent
