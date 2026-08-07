"""add finance and driver models"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, Sequence[str], None] = "b967af350de7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

U = lambda: postgresql.UUID(as_uuid=True)
T = lambda: sa.DateTime(timezone=True)


def audit() -> list:
    return [
        sa.Column("created_at", T(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", T(), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "expenses",
        sa.Column("id", U(), primary_key=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="CASH"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PAID"),
        sa.Column("reference_no", sa.String(100), nullable=True),
        *audit(),
    )

    op.create_table(
        "salaries",
        sa.Column("id", U(), primary_key=True),
        sa.Column("employee_name", sa.String(255), nullable=False),
        sa.Column("employee_id", sa.String(100), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False, server_default="BANK_TRANSFER"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("payment_date", sa.Date(), nullable=True),
        *audit(),
    )

    op.create_table(
        "drivers",
        sa.Column("id", U(), primary_key=True),
        sa.Column("driver_name", sa.String(255), nullable=False),
        sa.Column("license_number", sa.String(100), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("experience", sa.Integer(), nullable=True),
        sa.Column("bus_id", U(), sa.ForeignKey("buses.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        *audit(),
    )
    op.create_index("ix_drivers_bus_id", "drivers", ["bus_id"])


def downgrade() -> None:
    op.drop_index("ix_drivers_bus_id", table_name="drivers")
    op.drop_table("drivers")
    op.drop_table("salaries")
    op.drop_table("expenses")
