"""create and seed modules

Revision ID: a2f3c5d9e781
Revises: 4a9c2e7b8f01
Create Date: 2026-05-23 00:00:01.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a2f3c5d9e781"
down_revision: Union[str, None] = "4a9c2e7b8f01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


modules_table = sa.table(
    "modules",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
    sa.column("icon", sa.String),
    sa.column("color", sa.String),
    sa.column("route", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("sort_order", sa.Integer),
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("icon", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("route", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_modules_id"), "modules", ["id"], unique=False)
    op.create_index(op.f("ix_modules_slug"), "modules", ["slug"], unique=True)

    op.bulk_insert(
        modules_table,
        [
            {
                "name": "Account Management",
                "slug": "account-management",
                "icon": "users",
                "color": "#3b82f6",
                "route": "/accounts",
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Operations",
                "slug": "operations",
                "icon": "ship",
                "color": "#0ea5e9",
                "route": None,
                "is_active": False,
                "sort_order": 2,
            },
            {
                "name": "Finance",
                "slug": "finance",
                "icon": "wallet",
                "color": "#059669",
                "route": None,
                "is_active": False,
                "sort_order": 3,
            },
            {
                "name": "Sales",
                "slug": "sales",
                "icon": "shopping-cart",
                "color": "#f59e0b",
                "route": None,
                "is_active": False,
                "sort_order": 4,
            },
            {
                "name": "Marketing",
                "slug": "marketing",
                "icon": "bar-chart-3",
                "color": "#c026d3",
                "route": None,
                "is_active": False,
                "sort_order": 5,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_modules_slug"), table_name="modules")
    op.drop_index(op.f("ix_modules_id"), table_name="modules")
    op.drop_table("modules")
