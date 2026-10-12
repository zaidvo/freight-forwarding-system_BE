from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.modules.indenting.model import (
    IndentingCommissionPayer,
    IndentingCommissionType,
    IndentingDealStatus,
    IndentingPartyStatus,
)


# ─── Party Schemas ─────────────────────────────────────────────────────────────

class IndentingPartyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    contact_person: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=300)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    tax_id: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=1000)


class IndentingPartyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    contact_person: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=300)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    tax_id: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=1000)
    status: IndentingPartyStatus | None = None


class IndentingPartyRead(BaseModel):
    id: int
    code: str
    name: str
    normalized_name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    country: str | None
    tax_id: str | None
    notes: str | None
    status: IndentingPartyStatus
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IndentingPartySuggest(BaseModel):
    id: int
    code: str
    name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    city: str | None
    country: str | None

    model_config = {"from_attributes": True}


# ─── Payment Schemas ───────────────────────────────────────────────────────────

class IndentingCommissionPaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=1, max_length=10)
    payment_date: date
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=500)


class IndentingCommissionPaymentRead(BaseModel):
    id: int
    deal_id: int
    amount: Decimal
    currency: str
    payment_date: date
    reference: str | None
    notes: str | None
    created_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Deal Schemas ──────────────────────────────────────────────────────────────

class IndentingDealCreate(BaseModel):
    party_a_id: int
    party_b_id: int
    product: str = Field(min_length=1, max_length=200)
    quantity: Decimal = Field(gt=0)
    unit: str = Field(min_length=1, max_length=30)
    deal_value: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=1, max_length=10)
    deal_date: date
    commission_type: IndentingCommissionType
    commission_rate: Decimal | None = Field(default=None, ge=0)
    commission_amount: Decimal | None = Field(default=None, ge=0)
    commission_currency: str = Field(default="USD", min_length=1, max_length=10)
    commission_payer: IndentingCommissionPayer
    remarks: str | None = Field(default=None, max_length=1000)


class IndentingDealUpdate(BaseModel):
    party_a_id: int | None = None
    party_b_id: int | None = None
    product: str | None = Field(default=None, min_length=1, max_length=200)
    quantity: Decimal | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    deal_value: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=1, max_length=10)
    deal_date: date | None = None
    status: IndentingDealStatus | None = None
    commission_type: IndentingCommissionType | None = None
    commission_rate: Decimal | None = Field(default=None, ge=0)
    commission_amount: Decimal | None = Field(default=None, ge=0)
    commission_currency: str | None = Field(default=None, min_length=1, max_length=10)
    commission_payer: IndentingCommissionPayer | None = None
    remarks: str | None = Field(default=None, max_length=1000)


class IndentingDealStatusUpdate(BaseModel):
    status: IndentingDealStatus


class IndentingDealRead(BaseModel):
    id: int
    reference: str
    party_a_id: int
    party_b_id: int
    party_a: IndentingPartyRead | None = None
    party_b: IndentingPartyRead | None = None
    product: str
    quantity: Decimal
    unit: str
    deal_value: Decimal
    currency: str
    deal_date: date
    status: IndentingDealStatus
    commission_type: IndentingCommissionType
    commission_rate: Decimal | None
    commission_amount: Decimal
    commission_currency: str
    commission_payer: IndentingCommissionPayer
    remarks: str | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    # Dynamically calculated fields
    payment_status: str  # "pending", "partial", "paid", "overpaid"
    total_paid: Decimal
    balance_due: Decimal
    payments: list[IndentingCommissionPaymentRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ─── Summary Schemas ───────────────────────────────────────────────────────────

class CurrencySummaryItem(BaseModel):
    currency: str
    total_deal_value: Decimal
    expected_commission: Decimal
    received_commission: Decimal
    pending_commission: Decimal
    deal_count: int


class IndentingSummaryResponse(BaseModel):
    currencies: list[CurrencySummaryItem]
    total_deals: int
    active_parties: int
