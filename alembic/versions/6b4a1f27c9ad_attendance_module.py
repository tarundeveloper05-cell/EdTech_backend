"""attendance module

Revision ID: 6b4a1f27c9ad
Revises: 2a8d5c0f9b31
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "6b4a1f27c9ad"
down_revision: Union[str, Sequence[str], None] = "2a8d5c0f9b31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    attendance_status = postgresql.ENUM(
        "PRESENT",
        "ABSENT",
        "LATE",
        name="attendance_status",
        create_type=False,
    )
    attendance_status.create(op.get_bind(), checkfirst=True)

    op.add_column("students", sa.Column("class_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_students_class_id_classes", "students", "classes", ["class_id"], ["id"]
    )

    op.create_table(
        "attendance",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("class_id", sa.UUID(), nullable=False),
        sa.Column("subject_id", sa.UUID(), nullable=False),
        sa.Column("teacher_id", sa.UUID(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("period_no", sa.Integer(), nullable=False),
        sa.Column("status", attendance_status, nullable=False),
        sa.Column("marked_by", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"]),
        sa.ForeignKeyConstraint(["marked_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id", "attendance_date", "period_no", "subject_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("attendance")
    op.drop_constraint("fk_students_class_id_classes", "students", type_="foreignkey")
    op.drop_column("students", "class_id")
    sa.Enum(name="attendance_status").drop(op.get_bind(), checkfirst=True)
