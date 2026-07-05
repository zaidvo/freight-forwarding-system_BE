"""add trading import record metadata

Revision ID: e4c2a91f7d35
Revises: d8f1b42c6a90
Create Date: 2026-07-05 16:05:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4c2a91f7d35"
down_revision: Union[str, None] = "d8f1b42c6a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("trading_sales_import_records", sa.Column("customer", sa.String(length=180), nullable=True))
    op.add_column("trading_sales_import_records", sa.Column("salesperson", sa.String(length=150), nullable=True))
    op.add_column("trading_sales_import_records", sa.Column("company", sa.String(length=180), nullable=True))
    op.add_column("trading_sales_import_records", sa.Column("expected_arrival_date", sa.Date(), nullable=True))
    op.add_column("trading_sales_import_records", sa.Column("remarks", sa.String(length=1000), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("trading_sales_import_records", "remarks")
    op.drop_column("trading_sales_import_records", "expected_arrival_date")
    op.drop_column("trading_sales_import_records", "company")
    op.drop_column("trading_sales_import_records", "salesperson")
    op.drop_column("trading_sales_import_records", "customer")
