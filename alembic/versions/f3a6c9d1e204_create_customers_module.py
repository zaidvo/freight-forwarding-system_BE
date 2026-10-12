"""create shared customers module

Revision ID: f3a6c9d1e204
Revises: e4c2a91f7d35
Create Date: 2026-10-12 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "f3a6c9d1e204"
down_revision: Union[str, None] = "05bb42537510"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    customer_status_enum = postgresql.ENUM(
        "active", "inactive", name="customer_status_enum", create_type=False
    )
    customer_role_enum = postgresql.ENUM(
        "customer",
        "shipper",
        "consignee",
        "clearing_agent",
        name="customer_role_enum",
        create_type=False,
    )
    customer_status_enum.create(bind, checkfirst=True)
    customer_role_enum.create(bind, checkfirst=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("normalized_name", sa.String(length=180), nullable=False),
        sa.Column("contact_person", sa.String(length=150), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("tax_id", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("status", customer_status_enum, nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_customers_id", "customers", ["id"], unique=False)
    op.create_index("ix_customers_code", "customers", ["code"], unique=False)
    op.create_index("ix_customers_created_by", "customers", ["created_by"], unique=False)
    op.create_index("ix_customers_name_search", "customers", ["normalized_name"], unique=False)
    op.create_index("ix_customers_status_name", "customers", ["status", "name"], unique=False)

    op.create_table(
        "customer_roles",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("role", customer_role_enum, nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("customer_id", "role"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.drop_table("customer_roles")
    for index_name in (
        "ix_customers_status_name",
        "ix_customers_name_search",
        "ix_customers_created_by",
        "ix_customers_code",
        "ix_customers_id",
    ):
        op.drop_index(index_name, table_name="customers")
    op.drop_table("customers")
    postgresql.ENUM(name="customer_role_enum").drop(bind, checkfirst=True)
    postgresql.ENUM(name="customer_status_enum").drop(bind, checkfirst=True)
