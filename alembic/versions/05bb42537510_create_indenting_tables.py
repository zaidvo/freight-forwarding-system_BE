"""create indenting tables

Revision ID: 05bb42537510
Revises: e4c2a91f7d35
Create Date: 2026-10-12 20:26:45.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "05bb42537510"
down_revision: Union[str, None] = "e4c2a91f7d35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    party_status_enum = postgresql.ENUM(
        "active",
        "inactive",
        name="indenting_party_status_enum",
        create_type=False,
    )
    deal_status_enum = postgresql.ENUM(
        "open",
        "confirmed",
        "closed",
        "cancelled",
        name="indenting_deal_status_enum",
        create_type=False,
    )
    commission_type_enum = postgresql.ENUM(
        "percent",
        "fixed",
        name="indenting_commission_type_enum",
        create_type=False,
    )
    commission_payer_enum = postgresql.ENUM(
        "party_a",
        "party_b",
        "both",
        name="indenting_commission_payer_enum",
        create_type=False,
    )

    party_status_enum.create(op.get_bind(), checkfirst=True)
    deal_status_enum.create(op.get_bind(), checkfirst=True)
    commission_type_enum.create(op.get_bind(), checkfirst=True)
    commission_payer_enum.create(op.get_bind(), checkfirst=True)

    # 1. indenting_parties
    op.create_table(
        "indenting_parties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("normalized_name", sa.String(length=180), nullable=False),
        sa.Column("contact_person", sa.String(length=150), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("tax_id", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("status", party_status_enum, nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_indenting_parties_id"), "indenting_parties", ["id"], unique=False)
    op.create_index(op.f("ix_indenting_parties_code"), "indenting_parties", ["code"], unique=True)
    op.create_index(op.f("ix_indenting_parties_normalized_name"), "indenting_parties", ["normalized_name"], unique=False)
    op.create_index(op.f("ix_indenting_parties_created_by"), "indenting_parties", ["created_by"], unique=False)

    # 2. indenting_deals
    op.create_table(
        "indenting_deals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reference", sa.String(length=80), nullable=False),
        sa.Column("party_a_id", sa.Integer(), nullable=False),
        sa.Column("party_b_id", sa.Integer(), nullable=False),
        sa.Column("product", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column("deal_value", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("deal_date", sa.Date(), nullable=False),
        sa.Column("status", deal_status_enum, nullable=False),
        sa.Column("commission_type", commission_type_enum, nullable=False),
        sa.Column("commission_rate", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("commission_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("commission_currency", sa.String(length=10), nullable=False),
        sa.Column("commission_payer", commission_payer_enum, nullable=False),
        sa.Column("remarks", sa.String(length=1000), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["party_a_id"], ["indenting_parties.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["party_b_id"], ["indenting_parties.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    op.create_index(op.f("ix_indenting_deals_id"), "indenting_deals", ["id"], unique=False)
    op.create_index(op.f("ix_indenting_deals_reference"), "indenting_deals", ["reference"], unique=True)
    op.create_index(op.f("ix_indenting_deals_party_a_id"), "indenting_deals", ["party_a_id"], unique=False)
    op.create_index(op.f("ix_indenting_deals_party_b_id"), "indenting_deals", ["party_b_id"], unique=False)
    op.create_index(op.f("ix_indenting_deals_created_by"), "indenting_deals", ["created_by"], unique=False)

    # 3. indenting_commission_payments
    op.create_table(
        "indenting_commission_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("deal_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["deal_id"], ["indenting_deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_indenting_commission_payments_id"), "indenting_commission_payments", ["id"], unique=False)
    op.create_index(op.f("ix_indenting_commission_payments_deal_id"), "indenting_commission_payments", ["deal_id"], unique=False)
    op.create_index(op.f("ix_indenting_commission_payments_created_by"), "indenting_commission_payments", ["created_by"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("indenting_commission_payments")
    op.drop_table("indenting_deals")
    op.drop_table("indenting_parties")

    op.execute("DROP TYPE IF EXISTS indenting_commission_payer_enum")
    op.execute("DROP TYPE IF EXISTS indenting_commission_type_enum")
    op.execute("DROP TYPE IF EXISTS indenting_deal_status_enum")
    op.execute("DROP TYPE IF EXISTS indenting_party_status_enum")
