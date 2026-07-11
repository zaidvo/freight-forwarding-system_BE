from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.modules.trading_import.model import TradingImportDocumentType, TradingImportRecordStatus


class TradingImportRecordCreate(BaseModel):
    reference_no: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, max_length=180)
    customer: str | None = Field(default=None, max_length=180)
    salesperson: str | None = Field(default=None, max_length=150)
    company: str | None = Field(default=None, max_length=180)
    expected_arrival_date: date | None = None
    remarks: str | None = Field(default=None, max_length=1000)


class TradingImportRecordUpdate(BaseModel):
    reference_no: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, max_length=180)
    customer: str | None = Field(default=None, max_length=180)
    salesperson: str | None = Field(default=None, max_length=150)
    company: str | None = Field(default=None, max_length=180)
    expected_arrival_date: date | None = None
    remarks: str | None = Field(default=None, max_length=1000)
    status: TradingImportRecordStatus | None = None


class TradingSalesDocumentRead(BaseModel):
    id: int
    record_id: int
    document_type: TradingImportDocumentType
    original_filename: str
    stored_filename: str
    storage_path: str
    content_type: str | None
    file_size: int
    uploaded_by: int | None
    uploaded_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class TradingSalesFormUpsert(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)
    completed: bool = True


class TradingSalesFormRead(BaseModel):
    id: int
    record_id: int
    document_type: TradingImportDocumentType
    data: dict[str, Any]
    canonical_data: dict[str, Any]
    completed_by: int | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FreightChargeLine(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    label: str = Field(min_length=1, max_length=120)
    amount: Decimal = Field(ge=0)
    currency: str = Field(default="PKR", max_length=10)
    notes: str | None = Field(default=None, max_length=500)


class TradingSalesFreightInvoiceUpsert(BaseModel):
    invoice_no: str | None = Field(default=None, max_length=80)
    charges: list[FreightChargeLine] = Field(default_factory=list)
    manual_fields: dict[str, Any] = Field(default_factory=dict)


class TradingSalesFreightInvoiceRead(BaseModel):
    id: int
    record_id: int
    invoice_no: str | None
    charges: list[dict[str, Any]]
    manual_fields: dict[str, Any]
    render_data: dict[str, Any]
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TradingSalesPaymentReceiptCreate(BaseModel):
    receipt_no: str | None = Field(default=None, max_length=80)
    tid: str = Field(min_length=1, max_length=120)
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="PKR", max_length=10)
    payment_date: date | None = None


class TradingSalesPaymentReceiptRead(BaseModel):
    id: int
    record_id: int
    receipt_no: str | None
    tid: str
    amount: Decimal
    currency: str
    payment_date: date | None
    render_data: dict[str, Any]
    created_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TradingSalesDetentionInvoiceUpsert(BaseModel):
    invoice_no: str | None = Field(default=None, max_length=80)
    detention_start: date
    detention_end: date
    free_days: int = Field(default=0, ge=0)
    per_day_amount: Decimal = Field(default=0, ge=0)
    security_deposit: Decimal = Field(default=0, ge=0)
    currency: str = Field(default="PKR", max_length=10)
    manual_fields: dict[str, Any] = Field(default_factory=dict)


class TradingSalesDetentionInvoiceRead(BaseModel):
    id: int
    record_id: int
    invoice_no: str | None
    detention_start: date
    detention_end: date
    free_days: int
    chargeable_days: int
    per_day_amount: Decimal
    detention_amount: Decimal
    security_deposit: Decimal
    refund_amount: Decimal
    currency: str
    manual_fields: dict[str, Any]
    render_data: dict[str, Any]
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TradingImportRecordRead(BaseModel):
    id: int
    reference_no: str | None
    title: str | None
    customer: str | None
    salesperson: str | None
    company: str | None
    expected_arrival_date: date | None
    remarks: str | None
    status: TradingImportRecordStatus
    created_by: int | None
    created_at: datetime
    updated_at: datetime
    documents: list[TradingSalesDocumentRead] = Field(default_factory=list)
    forms: list[TradingSalesFormRead] = Field(default_factory=list)
    freight_invoice: TradingSalesFreightInvoiceRead | None = None
    payment_receipts: list[TradingSalesPaymentReceiptRead] = Field(default_factory=list)
    detention_invoice: TradingSalesDetentionInvoiceRead | None = None

    model_config = {"from_attributes": True}
