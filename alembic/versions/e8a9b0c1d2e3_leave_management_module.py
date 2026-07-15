"""leave management module

Revision ID: e8a9b0c1d2e3
Revises: d5f6a7b8c901
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "d5f6a7b8c901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum_create = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        "CANCELLED",
        name="leave_status",
    )
    status_enum_create.create(op.get_bind(), checkfirst=True)
    status_enum = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "REJECTED",
        "CANCELLED",
        name="leave_status",
        create_type=False,
    )

    op.create_table(
        "leave_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("leave_type_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("leave_type_name"),
    )
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("leave_type_id", sa.UUID(), nullable=False),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("to_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column(
            "applied_on",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("approved_by", sa.UUID(), nullable=True),
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
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["leave_type_id"], ["leave_types.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("leave_requests")
    op.drop_table("leave_types")
    sa.Enum(name="leave_status").drop(op.get_bind(), checkfirst=True)
