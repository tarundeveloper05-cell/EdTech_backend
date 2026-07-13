"""fee management module

Revision ID: a7e5b9c1d203
Revises: c4d2a6e8f091
"""
from alembic import op
import sqlalchemy as sa

revision = "a7e5b9c1d203"
down_revision = "c4d2a6e8f091"
branch_labels = None
depends_on = None


def _timestamps():
    return [sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False)]


def upgrade():
    op.create_table("fee_structures", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("fee_type", sa.String(100), nullable=False), sa.Column("description", sa.Text()), sa.Column("amount", sa.Numeric(10, 2), nullable=False), *_timestamps(), sa.UniqueConstraint("fee_type"))
    op.create_table("fee_invoices", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("student_id", sa.UUID(), nullable=False), sa.Column("fee_type_id", sa.UUID(), nullable=False), sa.Column("invoice_date", sa.Date(), nullable=False), sa.Column("due_date", sa.Date(), nullable=False), sa.Column("amount", sa.Numeric(10, 2), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="UNPAID"), *_timestamps(), sa.ForeignKeyConstraint(["student_id"], ["students.id"]), sa.ForeignKeyConstraint(["fee_type_id"], ["fee_structures.id"]))
    op.create_table("payments", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("invoice_id", sa.UUID(), nullable=False), sa.Column("payment_date", sa.Date(), nullable=False), sa.Column("amount_paid", sa.Numeric(10, 2), nullable=False), sa.Column("payment_method", sa.String(20), nullable=False), sa.Column("transaction_no", sa.String(100)), sa.Column("receipt_no", sa.String(100)), sa.Column("remarks", sa.Text()), *_timestamps(), sa.ForeignKeyConstraint(["invoice_id"], ["fee_invoices.id"]))


def downgrade():
    op.drop_table("payments")
    op.drop_table("fee_invoices")
    op.drop_table("fee_structures")
