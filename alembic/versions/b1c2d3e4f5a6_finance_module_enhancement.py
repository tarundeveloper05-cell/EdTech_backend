"""enhance finance module with complete fee management

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f7
Create Date: 2026-08-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import ForeignKey

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

U = lambda: postgresql.UUID(as_uuid=True)
T = lambda: sa.DateTime(timezone=True)
N = lambda p, s: sa.Numeric(p, s)


def _timestamps():
    return [
        sa.Column("created_at", T(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", T(), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    # 1. Drop existing unique constraint on fee_structures.fee_type
    op.drop_constraint("fee_structures_fee_type_key", "fee_structures", type_="unique")

    # 2. Add new columns to fee_structures (no foreign keys yet)
    op.add_column("fee_structures", sa.Column("academic_year", sa.String(20), nullable=True))
    op.add_column("fee_structures", sa.Column("section", sa.String(50), nullable=True))
    op.add_column("fee_structures", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("fee_structures", sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("fee_structures", sa.Column("max_discount_percentage", N(5, 2), nullable=True, server_default="0"))
    op.add_column("fee_structures", sa.Column("tax_percentage", N(5, 2), nullable=True, server_default="0"))

    # 3. Add new columns to fee_invoices (no foreign keys yet)
    op.add_column("fee_invoices", sa.Column("invoice_number", sa.String(100), nullable=True))
    op.add_column("fee_invoices", sa.Column("discount_amount", N(12, 2), nullable=False, server_default="0"))
    op.add_column("fee_invoices", sa.Column("late_fee_amount", N(12, 2), nullable=False, server_default="0"))
    op.add_column("fee_invoices", sa.Column("scholarship_amount", N(12, 2), nullable=False, server_default="0"))
    op.add_column("fee_invoices", sa.Column("net_amount", N(12, 2), nullable=True))
    op.alter_column("fee_invoices", "amount", existing_type=N(10, 2), type_=N(12, 2))

    # 4. Add new columns to payments (no foreign keys yet)
    op.add_column("payments", sa.Column("payment_status", sa.String(20), nullable=False, server_default="COMPLETED"))
    op.add_column("payments", sa.Column("receipt_number", sa.String(100), nullable=True))
    op.add_column("payments", sa.Column("gateway_response", sa.Text(), nullable=True))
    op.alter_column("payments", "amount_paid", existing_type=N(10, 2), type_=N(12, 2))
    op.alter_column("payments", "payment_method", existing_type=sa.String(20), type_=sa.String(20))

    # 5. Add new columns to expenses (no foreign keys yet)
    op.add_column("expenses", sa.Column("approval_status", sa.String(20), nullable=False, server_default="APPROVED"))
    op.add_column("expenses", sa.Column("attachment_path", sa.String(500), nullable=True))

    # 6. Add new columns to salaries (no foreign keys yet)
    op.add_column("salaries", sa.Column("approval_status", sa.String(20), nullable=False, server_default="APPROVED"))
    op.add_column("salaries", sa.Column("attachment_path", sa.String(500), nullable=True))

    # 7. Create student_categories table
    op.create_table(
        "student_categories",
        sa.Column("id", U(), primary_key=True),
        sa.Column("category_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("discount_percentage", N(5, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        *_timestamps(),
        sa.UniqueConstraint("category_name"),
    )

    # 8. Create fee_installments table
    op.create_table(
        "fee_installments",
        sa.Column("id", U(), primary_key=True),
        sa.Column("fee_structure_id", U(), ForeignKey("fee_structures.id"), nullable=False),
        sa.Column("installment_number", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("amount", N(10, 2), nullable=False),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default="false"),
        *_timestamps(),
        sa.UniqueConstraint("fee_structure_id", "installment_number", name="uq_installment_number"),
    )
    op.create_index("ix_fee_installments_fee_structure_id", "fee_installments", ["fee_structure_id"])

    # 9. Create student_fee_assignments table
    op.create_table(
        "student_fee_assignments",
        sa.Column("id", U(), primary_key=True),
        sa.Column("student_id", U(), ForeignKey("students.id"), nullable=False),
        sa.Column("fee_structure_id", U(), ForeignKey("fee_structures.id"), nullable=False),
        sa.Column("academic_year", sa.String(50), nullable=False),
        sa.Column("total_amount", N(12, 2), nullable=False),
        sa.Column("discount_amount", N(12, 2), nullable=False, server_default="0"),
        sa.Column("scholarship_amount", N(12, 2), nullable=False, server_default="0"),
        sa.Column("late_fee_amount", N(12, 2), nullable=False, server_default="0"),
        sa.Column("net_amount", N(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("student_category_id", U(), ForeignKey("student_categories.id"), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("student_id", "fee_structure_id", "academic_year", name="uq_student_fee_assignment"),
    )
    op.create_index("ix_student_fee_assignments_student_id", "student_fee_assignments", ["student_id"])
    op.create_index("ix_student_fee_assignments_fee_structure_id", "student_fee_assignments", ["fee_structure_id"])

    # 10. Create student_ledgers table
    op.create_table(
        "student_ledgers",
        sa.Column("id", U(), primary_key=True),
        sa.Column("student_id", U(), ForeignKey("students.id"), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("debit", N(12, 2), nullable=False, server_default="0"),
        sa.Column("credit", N(12, 2), nullable=False, server_default="0"),
        sa.Column("balance", N(12, 2), nullable=False, server_default="0"),
        sa.Column("transaction_type", sa.String(50), nullable=False),
        sa.Column("reference_id", U(), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("created_at", T(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_student_ledgers_student_id", "student_ledgers", ["student_id"])
    op.create_index("ix_student_ledgers_transaction_type", "student_ledgers", ["transaction_type"])

    # 11. Create scholarship_types table
    op.create_table(
        "scholarship_types",
        sa.Column("id", U(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(20), nullable=False, server_default="PERCENTAGE"),
        sa.Column("value", N(10, 2), nullable=False),
        sa.Column("approval_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("criteria", sa.Text(), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("name"),
    )

    # 12. Create student_scholarships table
    op.create_table(
        "student_scholarships",
        sa.Column("id", U(), primary_key=True),
        sa.Column("student_id", U(), ForeignKey("students.id"), nullable=False),
        sa.Column("scholarship_type_id", U(), ForeignKey("scholarship_types.id"), nullable=False),
        sa.Column("academic_year", sa.String(50), nullable=False),
        sa.Column("scholarship_amount", N(12, 2), nullable=False, server_default="0"),
        sa.Column("approved_amount", N(12, 2), nullable=True),
        sa.Column("approved_by", U(), ForeignKey("users.id"), nullable=True),
        sa.Column("approval_date", T(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("reason", sa.Text(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_student_scholarships_student_id", "student_scholarships", ["student_id"])
    op.create_index("ix_student_scholarships_scholarship_type_id", "student_scholarships", ["scholarship_type_id"])
    op.create_index("ix_student_scholarships_status", "student_scholarships", ["status"])

    # 13. Create late_fee_rules table
    op.create_table(
        "late_fee_rules",
        sa.Column("id", U(), primary_key=True),
        sa.Column("fee_structure_id", U(), ForeignKey("fee_structures.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(20), nullable=False, server_default="FIXED"),
        sa.Column("value", N(10, 2), nullable=False),
        sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("applicable_after_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        *_timestamps(),
    )
    op.create_index("ix_late_fee_rules_fee_structure_id", "late_fee_rules", ["fee_structure_id"])

    # 14. Create refund_requests table
    op.create_table(
        "refund_requests",
        sa.Column("id", U(), primary_key=True),
        sa.Column("student_id", U(), ForeignKey("students.id"), nullable=False),
        sa.Column("payment_id", U(), ForeignKey("payments.id"), nullable=True),
        sa.Column("invoice_id", U(), ForeignKey("fee_invoices.id"), nullable=True),
        sa.Column("amount", N(12, 2), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("approved_by", U(), ForeignKey("users.id"), nullable=True),
        sa.Column("approval_date", T(), nullable=True),
        sa.Column("processed_date", T(), nullable=True),
        sa.Column("transaction_no", sa.String(100), nullable=True),
        sa.Column("created_by", U(), ForeignKey("users.id"), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_refund_requests_student_id", "refund_requests", ["student_id"])
    op.create_index("ix_refund_requests_status", "refund_requests", ["status"])

    # 15. Create other_incomes table
    op.create_table(
        "other_incomes",
        sa.Column("id", U(), primary_key=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("amount", N(12, 2), nullable=False),
        sa.Column("income_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="CASH"),
        sa.Column("reference_no", sa.String(100), nullable=True),
        sa.Column("received_from", sa.String(255), nullable=True),
        sa.Column("created_by", U(), ForeignKey("users.id"), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_other_incomes_income_date", "other_incomes", ["income_date"])
    op.create_index("ix_other_incomes_category", "other_incomes", ["category"])

    # 16. Create expense_categories table
    op.create_table(
        "expense_categories",
        sa.Column("id", U(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        *_timestamps(),
        sa.UniqueConstraint("name"),
    )

    # 17. Now add foreign keys to existing tables (after new tables exist)
    op.add_column("fee_structures", sa.Column("class_id", U(), ForeignKey("classes.id"), nullable=True))
    op.add_column("fee_structures", sa.Column("student_category_id", U(), ForeignKey("student_categories.id"), nullable=True))

    op.add_column("fee_invoices", sa.Column("assignment_id", U(), ForeignKey("student_fee_assignments.id"), nullable=True))

    op.add_column("payments", sa.Column("processed_by", U(), ForeignKey("users.id"), nullable=True))

    op.add_column("expenses", sa.Column("expense_category_id", U(), ForeignKey("expense_categories.id"), nullable=True))
    op.add_column("expenses", sa.Column("approved_by", U(), ForeignKey("users.id"), nullable=True))
    op.add_column("expenses", sa.Column("created_by", U(), ForeignKey("users.id"), nullable=True))

    op.add_column("salaries", sa.Column("approved_by", U(), ForeignKey("users.id"), nullable=True))
    op.add_column("salaries", sa.Column("created_by", U(), ForeignKey("users.id"), nullable=True))

    # 18. Create indexes after columns are added
    op.create_index("ix_fee_structures_class_id", "fee_structures", ["class_id"])
    op.create_index("ix_fee_structures_student_category_id", "fee_structures", ["student_category_id"])
    op.create_unique_constraint(
        "uq_fee_structure_key", "fee_structures",
        ["fee_type", "academic_year", "class_id", "section", "student_category_id"],
    )
    op.create_index("ix_expenses_expense_category_id", "expenses", ["expense_category_id"])
    op.create_index("ix_expenses_approved_by", "expenses", ["approved_by"])
    op.create_index("ix_salaries_approved_by", "salaries", ["approved_by"])


def downgrade() -> None:
    # Remove foreign keys and columns from existing tables first
    op.drop_index("ix_salaries_approved_by", table_name="salaries")
    op.drop_column("salaries", "created_by")
    op.drop_column("salaries", "approved_by")
    op.drop_column("salaries", "attachment_path")
    op.drop_column("salaries", "approval_status")

    op.drop_index("ix_expenses_approved_by", table_name="expenses")
    op.drop_index("ix_expenses_expense_category_id", table_name="expenses")
    op.drop_column("expenses", "created_by")
    op.drop_column("expenses", "approved_by")
    op.drop_column("expenses", "expense_category_id")
    op.drop_column("expenses", "attachment_path")
    op.drop_column("expenses", "approval_status")

    op.drop_column("payments", "processed_by")
    op.drop_column("payments", "gateway_response")
    op.drop_column("payments", "receipt_number")
    op.drop_column("payments", "payment_status")
    op.alter_column("payments", "amount_paid", existing_type=N(12, 2), type_=N(10, 2))
    op.alter_column("payments", "payment_method", existing_type=sa.String(20), type_=sa.String(20))

    op.drop_index("ix_fee_invoices_assignment_id", table_name="fee_invoices")
    op.drop_column("fee_invoices", "assignment_id")
    op.drop_column("fee_invoices", "net_amount")
    op.drop_column("fee_invoices", "scholarship_amount")
    op.drop_column("fee_invoices", "late_fee_amount")
    op.drop_column("fee_invoices", "discount_amount")
    op.drop_column("fee_invoices", "invoice_number")
    op.alter_column("fee_invoices", "amount", existing_type=N(12, 2), type_=N(10, 2))

    op.drop_constraint("uq_fee_structure_key", "fee_structures", type_="unique")
    op.drop_index("ix_fee_structures_class_id", table_name="fee_structures")
    op.drop_index("ix_fee_structures_student_category_id", table_name="fee_structures")
    op.drop_column("fee_structures", "student_category_id")
    op.drop_column("fee_structures", "class_id")
    op.drop_column("fee_structures", "tax_percentage")
    op.drop_column("fee_structures", "max_discount_percentage")
    op.drop_column("fee_structures", "is_mandatory")
    op.drop_column("fee_structures", "is_active")
    op.drop_column("fee_structures", "section")
    op.drop_column("fee_structures", "academic_year")
    op.create_unique_constraint("fee_structures_fee_type_key", "fee_structures", ["fee_type"])

    # Drop new tables
    op.drop_table("expense_categories")
    op.drop_table("other_incomes")
    op.drop_table("refund_requests")
    op.drop_table("late_fee_rules")
    op.drop_table("student_scholarships")
    op.drop_table("scholarship_types")
    op.drop_table("student_ledgers")
    op.drop_table("student_fee_assignments")
    op.drop_table("fee_installments")
    op.drop_table("student_categories")
