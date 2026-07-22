"""hostel phase 1

Revision ID: aa1b2c3d4e5f
Revises: f8a2c5d7e9b3
Create Date: 2026-07-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "aa1b2c3d4e5f"
down_revision = "f8a2c5d7e9b3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("hostel_blocks", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("block_name", sa.String(255), nullable=False, unique=True), sa.Column("block_type", sa.String(100), nullable=False), sa.Column("total_floors", sa.Integer(), nullable=False), sa.Column("total_rooms", sa.Integer(), nullable=False), sa.Column("warden_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True), sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_table("hostel_rooms", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("block_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hostel_blocks.id"), nullable=False), sa.Column("room_no", sa.String(100), nullable=False), sa.Column("floor_no", sa.Integer(), nullable=False), sa.Column("capacity", sa.Integer(), nullable=False), sa.Column("occupancy", sa.Integer(), nullable=False, server_default="0"), sa.Column("status", sa.String(20), nullable=False, server_default="AVAILABLE"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.UniqueConstraint("block_id", "room_no", name="uq_hostel_rooms_block_room_no"))
    op.create_table("hostel_beds", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hostel_rooms.id"), nullable=False), sa.Column("bed_no", sa.String(100), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="VACANT"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.UniqueConstraint("room_id", "bed_no", name="uq_hostel_beds_room_bed_no"))
    op.create_table("hostel_allocations", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id"), nullable=False), sa.Column("bed_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hostel_beds.id"), nullable=False), sa.Column("check_in_date", sa.Date(), nullable=False), sa.Column("check_out_date", sa.Date(), nullable=True), sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("uq_hostel_allocations_active_student", "hostel_allocations", ["student_id"], unique=True, postgresql_where=sa.text("status = 'ACTIVE'"))
    op.create_index("uq_hostel_allocations_active_bed", "hostel_allocations", ["bed_id"], unique=True, postgresql_where=sa.text("status = 'ACTIVE'"))


def downgrade():
    op.drop_index("uq_hostel_allocations_active_bed", table_name="hostel_allocations")
    op.drop_index("uq_hostel_allocations_active_student", table_name="hostel_allocations")
    op.drop_table("hostel_allocations")
    op.drop_table("hostel_beds")
    op.drop_table("hostel_rooms")
    op.drop_table("hostel_blocks")
