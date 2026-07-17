"""library management module

Revision ID: c8d2e5f7a9b1
Revises: b3c7d1e4f6a8
Create Date: 2026-07-16 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c8d2e5f7a9b1"
down_revision: Union[str, Sequence[str], None] = "b3c7d1e4f6a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "book_categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("category_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_name"),
    )
    op.create_table(
        "books",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("isbn", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("rack_no", sa.String(length=100), nullable=True),
        sa.Column("total_copies", sa.Integer(), nullable=False),
        sa.Column("available_copies", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["book_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("isbn"),
    )
    op.create_table(
        "book_issues",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=True),
        sa.Column("fine_amount", sa.Numeric(precision=10, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'ISSUED'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("book_issues")
    op.drop_table("books")
    op.drop_table("book_categories")
