"""admissions module

Revision ID: d5f6a7b8c901
Revises: a7e5b9c1d203
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d5f6a7b8c901"
down_revision: Union[str, Sequence[str], None] = "a7e5b9c1d203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum_create = sa.Enum(
        "PENDING",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        name="admission_application_status",
    )
    status_enum_create.create(op.get_bind(), checkfirst=True)
    status_enum = postgresql.ENUM(
        "PENDING",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        name="admission_application_status",
        create_type=False,
    )

    op.create_table(
        "admission_applications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("applicant_name", sa.String(length=255), nullable=False),
        sa.Column("applied_class", sa.UUID(), nullable=False),
        sa.Column("application_date", sa.Date(), nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["applied_class"], ["classes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "admission_documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("application_id", sa.UUID(), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column(
            "verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("verified_by", sa.UUID(), nullable=True),
        sa.Column("verified_date", sa.Date(), nullable=True),
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
        sa.ForeignKeyConstraint(["application_id"], ["admission_applications.id"]),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("admission_documents")
    op.drop_table("admission_applications")
    sa.Enum(name="admission_application_status").drop(op.get_bind(), checkfirst=True)
