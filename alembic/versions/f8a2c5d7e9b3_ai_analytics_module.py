"""ai analytics module

Revision ID: f8a2c5d7e9b3
Revises: e4f7a9c2d6b1
Create Date: 2026-07-17 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f8a2c5d7e9b3"
down_revision: Union[str, Sequence[str], None] = "e4f7a9c2d6b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("ai_analytics",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("attendance_risk", sa.Numeric(precision=5, scale=2), nullable=False), sa.Column("performance_risk", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("predicted_grade", sa.String(length=10), nullable=True), sa.Column("learning_pattern", sa.Text(), nullable=True), sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("generated_on", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_analytics_student_id", "ai_analytics", ["student_id"])
    op.create_table("ai_chat_history",
        sa.Column("id", sa.UUID(), nullable=False), sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False), sa.Column("response", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_chat_history_user_id", "ai_chat_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_chat_history_user_id", table_name="ai_chat_history")
    op.drop_table("ai_chat_history")
    op.drop_index("ix_ai_analytics_student_id", table_name="ai_analytics")
    op.drop_table("ai_analytics")
