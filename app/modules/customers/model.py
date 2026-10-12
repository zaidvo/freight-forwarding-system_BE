from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLAEnum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CustomerRole(str, Enum):
    CUSTOMER = "customer"
    SHIPPER = "shipper"
    CONSIGNEE = "consignee"
    CLEARING_AGENT = "clearing_agent"


class CustomerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_name_search", "normalized_name"),
        Index("ix_customers_status_name", "status", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(180), nullable=False)
    contact_person: Mapped[str | None] = mapped_column(String(150))
    city: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(80))
    address: Mapped[str | None] = mapped_column(String(500))
    country: Mapped[str | None] = mapped_column(String(120))
    tax_id: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(String(1000))
    status: Mapped[CustomerStatus] = mapped_column(
        SQLAEnum(
            CustomerStatus,
            name="customer_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=CustomerStatus.ACTIVE,
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    role_links = relationship(
        "CustomerRoleLink",
        back_populates="customer",
        cascade="all, delete-orphan",
        order_by="CustomerRoleLink.role",
    )

    @property
    def roles(self) -> list[CustomerRole]:
        return [link.role for link in self.role_links]


class CustomerRoleLink(Base):
    __tablename__ = "customer_roles"

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[CustomerRole] = mapped_column(
        SQLAEnum(
            CustomerRole,
            name="customer_role_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        primary_key=True,
    )

    customer = relationship("Customer", back_populates="role_links")
