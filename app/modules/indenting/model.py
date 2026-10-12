from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLAEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IndentingPartyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class IndentingDealStatus(str, Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class IndentingCommissionType(str, Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class IndentingCommissionPayer(str, Enum):
    PARTY_A = "party_a"
    PARTY_B = "party_b"
    BOTH = "both"


class IndentingParty(Base):
    __tablename__ = "indenting_parties"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    contact_person: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    tax_id: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[IndentingPartyStatus] = mapped_column(
        SQLAEnum(
            IndentingPartyStatus,
            name="indenting_party_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=IndentingPartyStatus.ACTIVE,
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    deals_as_party_a = relationship(
        "IndentingDeal",
        foreign_keys="[IndentingDeal.party_a_id]",
        back_populates="party_a",
    )
    deals_as_party_b = relationship(
        "IndentingDeal",
        foreign_keys="[IndentingDeal.party_b_id]",
        back_populates="party_b",
    )


class IndentingDeal(Base):
    __tablename__ = "indenting_deals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    party_a_id: Mapped[int] = mapped_column(
        ForeignKey("indenting_parties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    party_b_id: Mapped[int] = mapped_column(
        ForeignKey("indenting_parties.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    product: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    deal_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    deal_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[IndentingDealStatus] = mapped_column(
        SQLAEnum(
            IndentingDealStatus,
            name="indenting_deal_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=IndentingDealStatus.OPEN,
        nullable=False,
    )
    commission_type: Mapped[IndentingCommissionType] = mapped_column(
        SQLAEnum(
            IndentingCommissionType,
            name="indenting_commission_type_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    commission_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    commission_currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    commission_payer: Mapped[IndentingCommissionPayer] = mapped_column(
        SQLAEnum(
            IndentingCommissionPayer,
            name="indenting_commission_payer_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    remarks: Mapped[str | None] = mapped_column(String(1000))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    party_a = relationship("IndentingParty", foreign_keys=[party_a_id], back_populates="deals_as_party_a")
    party_b = relationship("IndentingParty", foreign_keys=[party_b_id], back_populates="deals_as_party_b")
    payments = relationship(
        "IndentingCommissionPayment",
        back_populates="deal",
        cascade="all, delete-orphan",
        order_by="IndentingCommissionPayment.payment_date.asc(), IndentingCommissionPayment.id.asc()",
    )


class IndentingCommissionPayment(Base):
    __tablename__ = "indenting_commission_payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("indenting_deals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(String(500))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    deal = relationship("IndentingDeal", back_populates="payments")
