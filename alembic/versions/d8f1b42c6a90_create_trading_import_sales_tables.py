"""create trading import sales tables

Revision ID: d8f1b42c6a90
Revises: b7c4f92a10d2
Create Date: 2026-07-05 14:55:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d8f1b42c6a90"
down_revision: Union[str, None] = "b7c4f92a10d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    document_type_enum = postgresql.ENUM(
        "draft_bl",
        "house_bl",
        "master_bl",
        name="trading_import_document_type_enum",
        create_type=False,
    )
    record_status_enum = postgresql.ENUM(
        "draft",
        "in_progress",
        "ready_for_invoice",
        "invoiced",
        "paid",
        "detention",
        name="trading_import_record_status_enum",
        create_type=False,
    )

    document_type_enum.create(op.get_bind(), checkfirst=True)
    record_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "trading_sales_import_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reference_no", sa.String(length=80), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=True),
        sa.Column("status", record_status_enum, nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trading_sales_import_records_created_by"), "trading_sales_import_records", ["created_by"])
    op.create_index(op.f("ix_trading_sales_import_records_id"), "trading_sales_import_records", ["id"])
    op.create_index(
        op.f("ix_trading_sales_import_records_reference_no"),
        "trading_sales_import_records",
        ["reference_no"],
        unique=True,
    )

    op.create_table(
        "trading_sales_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=600), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["record_id"], ["trading_sales_import_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("record_id", "document_type", name="uq_trading_sales_document_record_type"),
    )
    op.create_index(op.f("ix_trading_sales_documents_document_type"), "trading_sales_documents", ["document_type"])
    op.create_index(op.f("ix_trading_sales_documents_id"), "trading_sales_documents", ["id"])
    op.create_index(op.f("ix_trading_sales_documents_record_id"), "trading_sales_documents", ["record_id"])
    op.create_index(op.f("ix_trading_sales_documents_uploaded_by"), "trading_sales_documents", ["uploaded_by"])

    op.create_table(
        "trading_sales_forms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("canonical_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("completed_by", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["completed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["record_id"], ["trading_sales_import_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("record_id", "document_type", name="uq_trading_sales_form_record_type"),
    )
    op.create_index(op.f("ix_trading_sales_forms_completed_by"), "trading_sales_forms", ["completed_by"])
    op.create_index(op.f("ix_trading_sales_forms_document_type"), "trading_sales_forms", ["document_type"])
    op.create_index(op.f("ix_trading_sales_forms_id"), "trading_sales_forms", ["id"])
    op.create_index(op.f("ix_trading_sales_forms_record_id"), "trading_sales_forms", ["record_id"])

    op.create_table(
        "trading_sales_freight_invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("invoice_no", sa.String(length=80), nullable=True),
        sa.Column("charges", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("manual_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("render_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["record_id"], ["trading_sales_import_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trading_sales_freight_invoices_created_by"), "trading_sales_freight_invoices", ["created_by"])
    op.create_index(op.f("ix_trading_sales_freight_invoices_id"), "trading_sales_freight_invoices", ["id"])
    op.create_index(
        op.f("ix_trading_sales_freight_invoices_invoice_no"),
        "trading_sales_freight_invoices",
        ["invoice_no"],
        unique=True,
    )
    op.create_index(
        op.f("ix_trading_sales_freight_invoices_record_id"),
        "trading_sales_freight_invoices",
        ["record_id"],
        unique=True,
    )

    op.create_table(
        "trading_sales_payment_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("receipt_no", sa.String(length=80), nullable=True),
        sa.Column("tid", sa.String(length=120), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("render_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["record_id"], ["trading_sales_import_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trading_sales_payment_receipts_created_by"), "trading_sales_payment_receipts", ["created_by"])
    op.create_index(op.f("ix_trading_sales_payment_receipts_id"), "trading_sales_payment_receipts", ["id"])
    op.create_index(
        op.f("ix_trading_sales_payment_receipts_receipt_no"),
        "trading_sales_payment_receipts",
        ["receipt_no"],
        unique=True,
    )
    op.create_index(op.f("ix_trading_sales_payment_receipts_record_id"), "trading_sales_payment_receipts", ["record_id"])

    op.create_table(
        "trading_sales_detention_invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("invoice_no", sa.String(length=80), nullable=True),
        sa.Column("detention_start", sa.Date(), nullable=False),
        sa.Column("detention_end", sa.Date(), nullable=False),
        sa.Column("free_days", sa.Integer(), nullable=False),
        sa.Column("chargeable_days", sa.Integer(), nullable=False),
        sa.Column("per_day_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("detention_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("security_deposit", sa.Numeric(14, 2), nullable=False),
        sa.Column("refund_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("manual_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("render_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["record_id"], ["trading_sales_import_records.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trading_sales_detention_invoices_created_by"), "trading_sales_detention_invoices", ["created_by"])
    op.create_index(op.f("ix_trading_sales_detention_invoices_id"), "trading_sales_detention_invoices", ["id"])
    op.create_index(
        op.f("ix_trading_sales_detention_invoices_invoice_no"),
        "trading_sales_detention_invoices",
        ["invoice_no"],
        unique=True,
    )
    op.create_index(
        op.f("ix_trading_sales_detention_invoices_record_id"),
        "trading_sales_detention_invoices",
        ["record_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_trading_sales_detention_invoices_record_id"), table_name="trading_sales_detention_invoices")
    op.drop_index(op.f("ix_trading_sales_detention_invoices_invoice_no"), table_name="trading_sales_detention_invoices")
    op.drop_index(op.f("ix_trading_sales_detention_invoices_id"), table_name="trading_sales_detention_invoices")
    op.drop_index(op.f("ix_trading_sales_detention_invoices_created_by"), table_name="trading_sales_detention_invoices")
    op.drop_table("trading_sales_detention_invoices")

    op.drop_index(op.f("ix_trading_sales_payment_receipts_record_id"), table_name="trading_sales_payment_receipts")
    op.drop_index(op.f("ix_trading_sales_payment_receipts_receipt_no"), table_name="trading_sales_payment_receipts")
    op.drop_index(op.f("ix_trading_sales_payment_receipts_id"), table_name="trading_sales_payment_receipts")
    op.drop_index(op.f("ix_trading_sales_payment_receipts_created_by"), table_name="trading_sales_payment_receipts")
    op.drop_table("trading_sales_payment_receipts")

    op.drop_index(op.f("ix_trading_sales_freight_invoices_record_id"), table_name="trading_sales_freight_invoices")
    op.drop_index(op.f("ix_trading_sales_freight_invoices_invoice_no"), table_name="trading_sales_freight_invoices")
    op.drop_index(op.f("ix_trading_sales_freight_invoices_id"), table_name="trading_sales_freight_invoices")
    op.drop_index(op.f("ix_trading_sales_freight_invoices_created_by"), table_name="trading_sales_freight_invoices")
    op.drop_table("trading_sales_freight_invoices")

    op.drop_index(op.f("ix_trading_sales_forms_record_id"), table_name="trading_sales_forms")
    op.drop_index(op.f("ix_trading_sales_forms_id"), table_name="trading_sales_forms")
    op.drop_index(op.f("ix_trading_sales_forms_document_type"), table_name="trading_sales_forms")
    op.drop_index(op.f("ix_trading_sales_forms_completed_by"), table_name="trading_sales_forms")
    op.drop_table("trading_sales_forms")

    op.drop_index(op.f("ix_trading_sales_documents_uploaded_by"), table_name="trading_sales_documents")
    op.drop_index(op.f("ix_trading_sales_documents_record_id"), table_name="trading_sales_documents")
    op.drop_index(op.f("ix_trading_sales_documents_id"), table_name="trading_sales_documents")
    op.drop_index(op.f("ix_trading_sales_documents_document_type"), table_name="trading_sales_documents")
    op.drop_table("trading_sales_documents")

    op.drop_index(op.f("ix_trading_sales_import_records_reference_no"), table_name="trading_sales_import_records")
    op.drop_index(op.f("ix_trading_sales_import_records_id"), table_name="trading_sales_import_records")
    op.drop_index(op.f("ix_trading_sales_import_records_created_by"), table_name="trading_sales_import_records")
    op.drop_table("trading_sales_import_records")

    document_type_enum = postgresql.ENUM(
        "draft_bl",
        "house_bl",
        "master_bl",
        name="trading_import_document_type_enum",
        create_type=False,
    )
    record_status_enum = postgresql.ENUM(
        "draft",
        "in_progress",
        "ready_for_invoice",
        "invoiced",
        "paid",
        "detention",
        name="trading_import_record_status_enum",
        create_type=False,
    )
    record_status_enum.drop(op.get_bind(), checkfirst=True)
    document_type_enum.drop(op.get_bind(), checkfirst=True)
