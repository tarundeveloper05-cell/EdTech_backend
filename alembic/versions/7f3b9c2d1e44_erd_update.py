"""erd update

Revision ID: 7f3b9c2d1e44
Revises: ee8d0b787c9c
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f3b9c2d1e44"
down_revision: Union[str, Sequence[str], None] = "ee8d0b787c9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("roles", "name", new_column_name="role_name")
    op.alter_column("roles", "description", type_=sa.Text())
    op.alter_column(
        "roles",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )

    op.execute(
        """
        INSERT INTO roles (id, role_name, description)
        VALUES
            ('00000000-0000-0000-0000-000000000001', 'ADMIN', 'Administrator'),
            ('00000000-0000-0000-0000-000000000002', 'TEACHER', 'Teacher'),
            ('00000000-0000-0000-0000-000000000003', 'PARENT', 'Parent'),
            ('00000000-0000-0000-0000-000000000004', 'STUDENT', 'Student')
        ON CONFLICT (role_name) DO NOTHING
        """
    )

    op.add_column("users", sa.Column("username", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column(
        "users",
        sa.Column("status", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column("users", sa.Column("last_login", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE users SET username = id::text WHERE username IS NULL")
    op.execute("UPDATE users SET status = is_active WHERE is_active IS NOT NULL")
    op.alter_column("users", "username", nullable=False)
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.drop_column("users", "first_name")
    op.drop_column("users", "last_name")
    op.drop_column("users", "is_active")

    op.create_table(
        "admins",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("admin_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "departments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("department_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("department_name"),
    )
    op.create_table(
        "teachers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("qualification", sa.String(length=255), nullable=True),
        sa.Column("department_id", sa.UUID(), nullable=True),
        sa.Column("join_date", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id"),
        sa.UniqueConstraint("user_id"),
    )

    op.add_column("parents", sa.Column("address", sa.Text(), nullable=True))
    op.create_unique_constraint("uq_parents_user_id", "parents", ["user_id"])

    op.add_column("students", sa.Column("admission_no", sa.String(length=50), nullable=True))
    op.add_column("students", sa.Column("first_name", sa.String(length=100), nullable=True))
    op.add_column("students", sa.Column("last_name", sa.String(length=100), nullable=True))
    op.add_column("students", sa.Column("blood_group", sa.String(length=10), nullable=True))
    op.add_column("students", sa.Column("roll_no", sa.String(length=50), nullable=True))
    op.add_column("students", sa.Column("joining_date", sa.Date(), nullable=True))
    op.add_column("students", sa.Column("photo", sa.String(length=500), nullable=True))
    op.execute("UPDATE students SET admission_no = admission_number")
    op.alter_column("students", "admission_no", nullable=False)
    op.create_unique_constraint("uq_students_user_id", "students", ["user_id"])
    op.create_unique_constraint("uq_students_admission_no", "students", ["admission_no"])
    op.drop_constraint("students_admission_number_key", "students", type_="unique")
    op.drop_column("students", "admission_number")
    op.drop_column("students", "date_of_birth")
    op.drop_column("students", "section")

    op.create_table(
        "parent_students",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("relationship", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["parents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("parent_id", "student_id", "relationship"),
    )
    op.execute(
        "INSERT INTO parent_students (id, parent_id, student_id) "
        "SELECT id, parent_id, student_id FROM student_parents"
    )
    op.drop_table("student_parents", schema="public")
    op.drop_table("faculty", schema="public")


def downgrade() -> None:
    op.create_table(
        "faculty",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("designation", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id"),
        schema="public",
    )
    op.create_table(
        "student_parents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["public.parents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["public.students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.drop_table("parent_students")
    op.add_column("students", sa.Column("section", sa.String(length=50), nullable=True))
    op.add_column("students", sa.Column("date_of_birth", sa.DateTime(), nullable=True))
    op.add_column("students", sa.Column("admission_number", sa.String(length=50), nullable=True))
    op.execute("UPDATE students SET admission_number = admission_no")
    op.alter_column("students", "admission_number", nullable=False)
    op.drop_constraint("uq_students_admission_no", "students", type_="unique")
    op.drop_constraint("uq_students_user_id", "students", type_="unique")
    op.create_unique_constraint("students_admission_number_key", "students", ["admission_number"])
    op.drop_column("students", "photo")
    op.drop_column("students", "joining_date")
    op.drop_column("students", "roll_no")
    op.drop_column("students", "blood_group")
    op.drop_column("students", "last_name")
    op.drop_column("students", "first_name")
    op.drop_column("students", "admission_no")
    op.drop_constraint("uq_parents_user_id", "parents", type_="unique")
    op.drop_column("parents", "address")
    op.drop_table("teachers")
    op.drop_table("departments")
    op.drop_table("admins")
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("first_name", sa.String(length=255), nullable=True))
    op.execute("UPDATE users SET is_active = status, first_name = username, last_name = username")
    op.alter_column("users", "is_active", nullable=False)
    op.alter_column("users", "last_name", nullable=False)
    op.alter_column("users", "first_name", nullable=False)
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_column("users", "last_login")
    op.drop_column("users", "status")
    op.drop_column("users", "phone")
    op.drop_column("users", "username")
    op.alter_column("roles", "role_name", new_column_name="name")
