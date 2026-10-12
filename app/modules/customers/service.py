import re
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.customers.model import Customer, CustomerRole, CustomerRoleLink, CustomerStatus
from app.modules.customers.repository import CustomerRepository
from app.modules.users.model import User


CORPORATE_SUFFIXES = {
    "co",
    "company",
    "corp",
    "corporation",
    "inc",
    "incorporated",
    "limited",
    "llc",
    "ltd",
    "pvt",
    "private",
}


def normalize_customer_name(name: str) -> str:
    value = name.casefold().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    words = [word for word in value.split() if word not in CORPORATE_SUFFIXES]
    return " ".join(words)


class CustomerService:
    def __init__(self, db: Session):
        self.repository = CustomerRepository(db)

    def list(self, **kwargs):
        return self.repository.list_customers(**kwargs)

    def suggest(self, query_text: str):
        return self.repository.suggest(query_text=query_text)

    def get(self, customer_id: int) -> Customer:
        customer = self.repository.get(customer_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer

    def duplicates(self, *, name: str, customer_id: int | None):
        normalized_name = normalize_customer_name(name)
        if not normalized_name:
            return []
        return self.repository.find_duplicates(
            normalized_name=normalized_name,
            customer_id=customer_id,
        )

    def create(self, *, payload, actor: User) -> Customer:
        customer = Customer(
            # The database assigns the numeric id during INSERT, while code is
            # non-null. Use a unique temporary value for that first flush; the
            # repository replaces it with the public CUS-xxxxx code before commit.
            code=f"TMP-{uuid4().hex[:15]}",
            name=payload.name.strip(),
            normalized_name=normalize_customer_name(payload.name),
            contact_person=payload.contact_person,
            city=payload.city,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
            country=payload.country,
            tax_id=payload.tax_id,
            notes=payload.notes,
            status=CustomerStatus.ACTIVE,
            created_by=actor.id,
        )
        customer.role_links = [CustomerRoleLink(role=role) for role in payload.roles]
        return self.repository.create(customer)

    def update(self, *, customer_id: int, payload) -> Customer:
        customer = self.get(customer_id)
        values = payload.model_dump(exclude_unset=True, exclude={"roles"})
        if "name" in values:
            values["name"] = values["name"].strip()
            values["normalized_name"] = normalize_customer_name(values["name"])
        for key, value in values.items():
            setattr(customer, key, value)
        if payload.roles is not None:
            customer.role_links = [CustomerRoleLink(role=role) for role in payload.roles]
        return self.repository.save(customer)

    def set_status(self, *, customer_id: int, active: bool) -> Customer:
        customer = self.get(customer_id)
        customer.status = CustomerStatus.ACTIVE if active else CustomerStatus.INACTIVE
        return self.repository.save(customer)
