"""rename super_admin role to root

Revision ID: 4a9c2e7b8f01
Revises: 9b7f2d4c1a83
Create Date: 2026-05-23 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4a9c2e7b8f01"
down_revision: Union[str, None] = "9b7f2d4c1a83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE user_role_enum RENAME VALUE 'super_admin' TO 'root'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE user_role_enum RENAME VALUE 'root' TO 'super_admin'")
