from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import Date, DateTime, Enum as SQLAEnum, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TradingImportDocumentType(str, Enum):
    DRAFT_BL = "draft_bl"
    HOUSE_BL = "house_bl"
    MASTER_BL = "master_bl"


class TradingImportRecordStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    READY_FOR_INVOICE = "ready_for_invoice"
    INVOICED = "invoiced"
    PAID = "paid"
    DETENTION = "detention"


class TradingSalesImportRecord(Base):
    __tablename__ = "trading_sales_import_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference_no: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(180))
    customer: Mapped[str | None] = mapped_column(String(180))
    salesperson: Mapped[str | None] = mapped_column(String(150))
    company: Mapped[str | None] = mapped_column(String(180))
    expected_arrival_date: Mapped[date | None] = mapped_column(Date)
    remarks: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[TradingImportRecordStatus] = mapped_column(
        SQLAEnum(
            TradingImportRecordStatus,
            name="trading_import_record_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TradingImportRecordStatus.DRAFT,
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    documents = relationship(
        "TradingSalesDocument",
        back_populates="record",
        cascade="all, delete-orphan",
        order_by="TradingSalesDocument.document_type",
    )
    forms = relationship(
        "TradingSalesForm",
        back_populates="record",
        cascade="all, delete-orphan",
        order_by="TradingSalesForm.document_type",
    )
    freight_invoice = relationship(
        "TradingSalesFreightInvoice",
        back_populates="record",
        cascade="all, delete-orphan",
        uselist=False,
    )
    payment_receipts = relationship(
        "TradingSalesPaymentReceipt",
        back_populates="record",
        cascade="all, delete-orphan",
        order_by="TradingSalesPaymentReceipt.created_at",
    )
    detention_invoice = relationship(
        "TradingSalesDetentionInvoice",
        back_populates="record",
        cascade="all, delete-orphan",
        uselist=False,
    )


class TradingSalesDocument(Base):
    __tablename__ = "trading_sales_documents"
    __table_args__ = (
        UniqueConstraint("record_id", "document_type", name="uq_trading_sales_document_record_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(
        ForeignKey("trading_sales_import_records.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    document_type: Mapped[TradingImportDocumentType] = mapped_column(
        SQLAEnum(
            TradingImportDocumentType,
            name="trading_import_document_type_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        index=True,
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(600), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120))
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    record = relationship("TradingSalesImportRecord", back_populates="documents")


class TradingSalesForm(Base):
    __tablename__ = "trading_sales_forms"
    __table_args__ = (
        UniqueConstraint("record_id", "document_type", name="uq_trading_sales_form_record_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(
        ForeignKey("trading_sales_import_records.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    document_type: Mapped[TradingImportDocumentType] = mapped_column(
        SQLAEnum(
            TradingImportDocumentType,
            name="trading_import_document_type_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        index=True,
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    canonical_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    completed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    record = relationship("TradingSalesImportRecord", back_populates="forms")


class TradingSalesFreightInvoice(Base):
    __tablename__ = "trading_sales_freight_invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(
        ForeignKey("trading_sales_import_records.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    invoice_no: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    charges: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    manual_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    render_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    record = relationship("TradingSalesImportRecord", back_populates="freight_invoice")


class TradingSalesPaymentReceipt(Base):
    __tablename__ = "trading_sales_payment_receipts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(
        ForeignKey("trading_sales_import_records.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    receipt_no: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    tid: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date)
    render_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    record = relationship("TradingSalesImportRecord", back_populates="payment_receipts")


class TradingSalesDetentionInvoice(Base):
    __tablename__ = "trading_sales_detention_invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    record_id: Mapped[int] = mapped_column(
        ForeignKey("trading_sales_import_records.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    invoice_no: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    detention_start: Mapped[date] = mapped_column(Date, nullable=False)
    detention_end: Mapped[date] = mapped_column(Date, nullable=False)
    free_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chargeable_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    per_day_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    detention_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    security_deposit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)
    manual_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    render_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    record = relationship("TradingSalesImportRecord", back_populates="detention_invoice")
