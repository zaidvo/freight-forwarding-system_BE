from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_module_access, require_root
from app.modules.indenting.model import IndentingDealStatus, IndentingPartyStatus
from app.modules.indenting.schemas import (
    IndentingCommissionPaymentCreate,
    IndentingDealCreate,
    IndentingDealStatusUpdate,
    IndentingDealUpdate,
    IndentingPartyCreate,
    IndentingPartyRead,
    IndentingPartySuggest,
    IndentingPartyUpdate,
)
from app.modules.indenting.service import IndentingService
from app.modules.users.model import User

router = APIRouter(prefix="/indenting", tags=["Indenting"])
require_indenting_access = require_module_access("indenting")


# ─── Parties ───────────────────────────────────────────────────────────────────

@router.get("/parties", summary="List indenting parties")
def list_parties(
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
    q: str | None = Query(default=None, description="Search by name, code, contact person, email, or phone"),
    status: IndentingPartyStatus | None = Query(default=None, description="Filter by party status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
):
    result = IndentingService(db).list_parties(
        q=q,
        status_value=status,
        page=page,
        page_size=page_size,
    )
    items = [IndentingPartyRead.model_validate(p).model_dump(mode="json") for p in result["items"]]
    return make_response(
        True,
        "Parties fetched successfully",
        {
            "items": items,
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
            "total_pages": result["total_pages"],
        },
    )


@router.get("/parties/suggest", summary="Suggest active parties for autocomplete")
def suggest_parties(
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
    q: str | None = Query(default=None, description="Query string"),
):
    parties = IndentingService(db).suggest_parties(q=q, limit=10)
    data = [IndentingPartySuggest.model_validate(p).model_dump(mode="json") for p in parties]
    return make_response(True, "Parties suggestions fetched", data)


@router.post("/parties", summary="Create indenting party")
def create_party(
    payload: IndentingPartyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_indenting_access),
):
    party = IndentingService(db).create_party(payload=payload, actor=current_user)
    return make_response(
        True,
        "Party created successfully",
        IndentingPartyRead.model_validate(party).model_dump(mode="json"),
    )


@router.get("/parties/{party_id}", summary="Get party details")
def get_party(
    party_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    party = IndentingService(db).get_party(party_id)
    return make_response(
        True,
        "Party fetched successfully",
        IndentingPartyRead.model_validate(party).model_dump(mode="json"),
    )


@router.put("/parties/{party_id}", summary="Update party details")
def update_party(
    party_id: int,
    payload: IndentingPartyUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    party = IndentingService(db).update_party(party_id=party_id, payload=payload)
    return make_response(
        True,
        "Party updated successfully",
        IndentingPartyRead.model_validate(party).model_dump(mode="json"),
    )


@router.patch("/parties/{party_id}/deactivate", summary="Deactivate party")
def deactivate_party(
    party_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    party = IndentingService(db).deactivate_party(party_id)
    return make_response(
        True,
        "Party deactivated successfully",
        IndentingPartyRead.model_validate(party).model_dump(mode="json"),
    )


@router.patch("/parties/{party_id}/activate", summary="Activate party")
def activate_party(
    party_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    party = IndentingService(db).activate_party(party_id)
    return make_response(
        True,
        "Party activated successfully",
        IndentingPartyRead.model_validate(party).model_dump(mode="json"),
    )


# ─── Deals ─────────────────────────────────────────────────────────────────────

@router.get("/deals", summary="List indenting deals")
def list_deals(
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
    q: str | None = Query(default=None, description="Search reference, product, remarks"),
    status: IndentingDealStatus | None = Query(default=None, description="Filter deal status"),
    party_id: int | None = Query(default=None, description="Filter by involved party"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
):
    result = IndentingService(db).list_deals(
        q=q,
        status_value=status,
        party_id=party_id,
        page=page,
        page_size=page_size,
    )
    return make_response(
        True,
        "Deals fetched successfully",
        result,
    )


@router.post("/deals", summary="Create indenting deal")
def create_deal(
    payload: IndentingDealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_indenting_access),
):
    deal = IndentingService(db).create_deal(payload=payload, actor=current_user)
    return make_response(True, "Deal created successfully", deal)


@router.get("/deals/{deal_id}", summary="Get deal details")
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    deal = IndentingService(db).get_deal(deal_id)
    return make_response(True, "Deal fetched successfully", deal)


@router.put("/deals/{deal_id}", summary="Update deal details")
def update_deal(
    deal_id: int,
    payload: IndentingDealUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    deal = IndentingService(db).update_deal(deal_id=deal_id, payload=payload)
    return make_response(True, "Deal updated successfully", deal)


@router.patch("/deals/{deal_id}/status", summary="Update deal status")
def update_deal_status(
    deal_id: int,
    payload: IndentingDealStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    deal = IndentingService(db).update_deal_status(deal_id=deal_id, new_status=payload.status)
    return make_response(True, "Deal status updated successfully", deal)


# ─── Payments ──────────────────────────────────────────────────────────────────

@router.get("/deals/{deal_id}/payments", summary="List deal commission payments")
def list_payments(
    deal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    deal = IndentingService(db).get_deal(deal_id)
    return make_response(True, "Payments fetched successfully", deal["payments"])


@router.post("/deals/{deal_id}/payments", summary="Add commission payment to deal")
def add_payment(
    deal_id: int,
    payload: IndentingCommissionPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_indenting_access),
):
    deal = IndentingService(db).add_payment(deal_id=deal_id, payload=payload, actor=current_user)
    return make_response(True, "Payment added successfully", deal)


@router.delete("/deals/{deal_id}/payments/{payment_id}", summary="Remove commission payment (Root only)")
def delete_payment(
    deal_id: int,
    payment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    deal = IndentingService(db).delete_payment(deal_id=deal_id, payment_id=payment_id)
    return make_response(True, "Payment removed successfully", deal)


# ─── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", summary="Indenting commission financial summary")
def get_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_indenting_access),
):
    summary = IndentingService(db).get_summary()
    return make_response(
        True,
        "Summary fetched successfully",
        summary.model_dump(mode="json"),
    )
