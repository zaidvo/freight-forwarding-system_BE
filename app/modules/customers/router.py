from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_module_access, require_root
from app.modules.customers.access import require_any_module_access
from app.modules.customers.model import CustomerRole, CustomerStatus
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerDuplicateCheck,
    CustomerListResponse,
    CustomerRead,
    CustomerSuggestionRead,
    CustomerUpdate,
)
from app.modules.customers.service import CustomerService
from app.modules.users.model import User


router = APIRouter(prefix="/customers", tags=["Customers"])
require_customer_module = require_module_access("customers")
require_customer_inline_access = require_any_module_access("customers", "operations", "sales")


@router.get("")
def list_customers(
    q: str | None = Query(default=None, max_length=120),
    role: CustomerRole | None = None,
    status: CustomerStatus | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(require_customer_module),
):
    items, total = CustomerService(db).list(
        query_text=q,
        role=role,
        status=status,
        page=page,
        page_size=page_size,
    )
    data = CustomerListResponse(
        items=[CustomerRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )
    return make_response(True, "Customers fetched successfully", data.model_dump(mode="json"))


@router.get("/suggest")
def suggest_customers(
    q: str = Query(min_length=1, max_length=120),
    db: Session = Depends(get_db),
    _: User = Depends(require_customer_inline_access),
):
    items = CustomerService(db).suggest(q)
    return make_response(
        True,
        "Customer suggestions fetched successfully",
        [CustomerSuggestionRead.model_validate(item).model_dump(mode="json") for item in items],
    )


@router.post("/check-duplicates")
def check_duplicates(
    payload: CustomerDuplicateCheck,
    db: Session = Depends(get_db),
    _: User = Depends(require_customer_inline_access),
):
    matches = CustomerService(db).duplicates(name=payload.name, customer_id=payload.customer_id)
    return make_response(
        True,
        "Duplicate check completed",
        [CustomerRead.model_validate(item).model_dump(mode="json") for item in matches],
    )


@router.post("")
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer_inline_access),
):
    customer = CustomerService(db).create(payload=payload, actor=current_user)
    return make_response(
        True,
        "Customer created successfully",
        CustomerRead.model_validate(customer).model_dump(mode="json"),
    )


@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_customer_inline_access),
):
    customer = CustomerService(db).get(customer_id)
    return make_response(
        True,
        "Customer fetched successfully",
        CustomerRead.model_validate(customer).model_dump(mode="json"),
    )


@router.put("/{customer_id}")
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    customer = CustomerService(db).update(customer_id=customer_id, payload=payload)
    return make_response(
        True,
        "Customer updated successfully",
        CustomerRead.model_validate(customer).model_dump(mode="json"),
    )


@router.patch("/{customer_id}/deactivate")
def deactivate_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    customer = CustomerService(db).set_status(customer_id=customer_id, active=False)
    return make_response(
        True,
        "Customer deactivated successfully",
        CustomerRead.model_validate(customer).model_dump(mode="json"),
    )


@router.patch("/{customer_id}/activate")
def activate_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    customer = CustomerService(db).set_status(customer_id=customer_id, active=True)
    return make_response(
        True,
        "Customer activated successfully",
        CustomerRead.model_validate(customer).model_dump(mode="json"),
    )
