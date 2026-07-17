"""transport management module

Revision ID: d9e3f6a8b2c4
Revises: c8d2e5f7a9b1
Create Date: 2026-07-16 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d9e3f6a8b2c4"
down_revision: Union[str, Sequence[str], None] = "c8d2e5f7a9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "buses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("bus_number", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bus_number"),
    )
    op.create_table(
        "routes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("route_name", sa.String(length=255), nullable=False),
        sa.Column("start_point", sa.String(length=255), nullable=False),
        sa.Column("end_point", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route_name"),
    )
    op.create_table(
        "student_transport",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("bus_id", sa.UUID(), nullable=False),
        sa.Column("route_id", sa.UUID(), nullable=False),
        sa.Column("stop_point", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["bus_id"], ["buses.id"]),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )


def downgrade() -> None:
    op.drop_table("student_transport")
    op.drop_table("routes")
    op.drop_table("buses")
