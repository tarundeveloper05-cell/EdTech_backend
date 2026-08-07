"""merge heads

Revision ID: 76fd73ec738f
Revises: a1b2c3d4e5f6, bb2c3d4e5f6a
Create Date: 2026-07-31 14:46:01.524226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76fd73ec738f'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'bb2c3d4e5f6a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
