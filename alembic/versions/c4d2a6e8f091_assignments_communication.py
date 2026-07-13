"""assignments and communication modules

Revision ID: c4d2a6e8f091
Revises: 9c1e7b3d4a62
"""
from alembic import op
import sqlalchemy as sa

revision = "c4d2a6e8f091"
down_revision = "9c1e7b3d4a62"
branch_labels = None
depends_on = None


def _timestamps():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade():
    op.create_table("assignments", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("teacher_id", sa.UUID(), nullable=False), sa.Column("class_id", sa.UUID(), nullable=False), sa.Column("subject_id", sa.UUID(), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("due_date", sa.DateTime(timezone=True), nullable=False), sa.Column("attachment", sa.String(500)), *_timestamps(), sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]), sa.ForeignKeyConstraint(["class_id"], ["classes.id"]), sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]))
    op.create_table("assignment_submissions", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("assignment_id", sa.UUID(), nullable=False), sa.Column("student_id", sa.UUID(), nullable=False), sa.Column("submitted_on", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("file_path", sa.String(500)), sa.Column("marks", sa.Numeric(10, 2)), sa.Column("remarks", sa.Text()), *_timestamps(), sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"]), sa.ForeignKeyConstraint(["student_id"], ["students.id"]), sa.UniqueConstraint("assignment_id", "student_id"))
    op.create_table("announcements", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("title", sa.String(255), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("target_audience", sa.String(20), nullable=False), sa.Column("created_by", sa.UUID(), nullable=False), *_timestamps(), sa.ForeignKeyConstraint(["created_by"], ["users.id"]))
    op.create_table("notifications", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("user_id", sa.UUID(), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("sent_on", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False), *_timestamps(), sa.ForeignKeyConstraint(["user_id"], ["users.id"]))
    op.create_table("messages", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("sender_id", sa.UUID(), nullable=False), sa.Column("receiver_id", sa.UUID(), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("sent_on", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False), *_timestamps(), sa.ForeignKeyConstraint(["sender_id"], ["users.id"]), sa.ForeignKeyConstraint(["receiver_id"], ["users.id"]))


def downgrade():
    op.drop_table("messages")
    op.drop_table("notifications")
    op.drop_table("announcements")
    op.drop_table("assignment_submissions")
    op.drop_table("assignments")
