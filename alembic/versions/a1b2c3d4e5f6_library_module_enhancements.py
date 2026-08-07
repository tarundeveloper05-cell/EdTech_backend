"""library module enhancements

Revision ID: a1b2c3d4e5f6
Revises: c8d2e5f7a9b1
Create Date: 2026-07-16 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from decimal import Decimal


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "c8d2e5f7a9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status column to book_categories
    op.add_column("book_categories", sa.Column("status", sa.Boolean(), nullable=False, server_default="true"))

    # Create library_authors
    op.create_table(
        "library_authors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("status", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Create library_publishers
    op.create_table(
        "library_publishers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_info", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("status", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Add new columns to books
    op.add_column("books", sa.Column("subtitle", sa.String(length=255), nullable=True))
    op.add_column("books", sa.Column("author_id", sa.UUID(), nullable=True))
    op.add_column("books", sa.Column("publisher_id", sa.UUID(), nullable=True))
    op.add_column("books", sa.Column("edition", sa.String(length=50), nullable=True))
    op.add_column("books", sa.Column("language", sa.String(length=50), nullable=True))
    op.add_column("books", sa.Column("rack_number", sa.String(length=100), nullable=True))
    op.add_column("books", sa.Column("shelf_number", sa.String(length=100), nullable=True))
    op.add_column("books", sa.Column("cover_image", sa.String(length=500), nullable=True))
    op.add_column("books", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("books", sa.Column("status", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("books", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"))
    op.create_foreign_key("books_author_id_fkey", "books", "library_authors", ["author_id"], ["id"])
    op.create_foreign_key("books_publisher_id_fkey", "books", "library_publishers", ["publisher_id"], ["id"])

    # Add fine_paid to book_issues
    op.add_column("book_issues", sa.Column("fine_paid", sa.Boolean(), nullable=False, server_default="false"))

    # Create book_reservations
    op.create_table(
        "book_reservations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("book_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("reservation_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("approval_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create library_settings
    op.create_table(
        "library_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("max_books_per_student", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("fine_per_day", sa.Numeric(precision=10, scale=2), nullable=False, server_default="10.00"),
        sa.Column("reservation_limit", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("borrow_duration", sa.Integer(), nullable=False, server_default="14"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create fine_payments
    op.create_table(
        "fine_payments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("issue_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("payment_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["book_issues.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("fine_payments")
    op.drop_table("library_settings")
    op.drop_table("book_reservations")
    op.drop_column("book_issues", "fine_paid")
    op.drop_constraint("books_publisher_id_fkey", "books", type_="foreignkey")
    op.drop_constraint("books_author_id_fkey", "books", type_="foreignkey")
    op.drop_column("books", "is_deleted")
    op.drop_column("books", "status")
    op.drop_column("books", "description")
    op.drop_column("books", "cover_image")
    op.drop_column("books", "shelf_number")
    op.drop_column("books", "rack_number")
    op.drop_column("books", "language")
    op.drop_column("books", "edition")
    op.drop_column("books", "publisher_id")
    op.drop_column("books", "author_id")
    op.drop_column("books", "subtitle")
    op.drop_table("library_publishers")
    op.drop_table("library_authors")
    op.drop_column("book_categories", "status")
