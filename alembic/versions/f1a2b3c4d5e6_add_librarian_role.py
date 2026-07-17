"""Add Librarian role

Revision ID: f1a2b3c4d5e6
Revises: ee8d0b787c9c
Create Date: 2026-07-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'e8a9b0c1d2e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles (id, role_name, description)
        VALUES
            ('00000000-0000-0000-0000-000000000006', 'LIBRARIAN', 'Librarian')
        ON CONFLICT (role_name) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM roles WHERE role_name = 'LIBRARIAN'
        """
    )
