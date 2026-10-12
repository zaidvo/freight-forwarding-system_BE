from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.modules.customers.model import CustomerRole, CustomerStatus


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    contact_person: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=80)
    address: str | None = Field(default=None, max_length=500)
    country: str | None = Field(default=None, max_length=120)
    tax_id: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)
    roles: list[CustomerRole] = Field(default_factory=lambda: [CustomerRole.CUSTOMER])

    @field_validator("roles")
    @classmethod
    def unique_roles(cls, value: list[CustomerRole]) -> list[CustomerRole]:
        return list(dict.fromkeys(value)) or [CustomerRole.CUSTOMER]


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    contact_person: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=80)
    address: str | None = Field(default=None, max_length=500)
    country: str | None = Field(default=None, max_length=120)
    tax_id: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)
    roles: list[CustomerRole] | None = None

    @field_validator("roles")
    @classmethod
    def unique_roles(cls, value: list[CustomerRole] | None) -> list[CustomerRole] | None:
        if value is None:
            return None
        return list(dict.fromkeys(value)) or [CustomerRole.CUSTOMER]


class CustomerRead(BaseModel):
    id: int
    code: str
    name: str
    normalized_name: str
    contact_person: str | None
    city: str | None
    email: str | None
    phone: str | None
    address: str | None
    country: str | None
    tax_id: str | None
    notes: str | None
    status: CustomerStatus
    roles: list[CustomerRole]
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerSuggestionRead(BaseModel):
    id: int
    code: str
    name: str
    contact_person: str | None
    city: str | None
    email: str | None
    phone: str | None
    address: str | None
    country: str | None
    roles: list[CustomerRole]
    status: CustomerStatus

    model_config = {"from_attributes": True}


class CustomerDuplicateCheck(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    customer_id: int | None = None


class CustomerListResponse(BaseModel):
    items: list[CustomerRead]
    page: int
    page_size: int
    total: int
