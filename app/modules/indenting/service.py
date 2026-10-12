from decimal import Decimal
from math import ceil
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.indenting.model import (
    IndentingCommissionType,
    IndentingDeal,
    IndentingDealStatus,
    IndentingParty,
    IndentingPartyStatus,
)
from app.modules.indenting.repository import IndentingRepository
from app.modules.indenting.schemas import (
    CurrencySummaryItem,
    IndentingCommissionPaymentCreate,
    IndentingDealCreate,
    IndentingDealRead,
    IndentingDealUpdate,
    IndentingPartyCreate,
    IndentingPartyUpdate,
    IndentingSummaryResponse,
)
from app.modules.users.model import User


class IndentingService:
    def __init__(self, db: Session):
        self.repository = IndentingRepository(db)

    # ─── Parties ───────────────────────────────────────────────────────────────

    def list_parties(
        self,
        *,
        q: str | None = None,
        status_value: IndentingPartyStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        total = self.repository.count_parties(q=q, status=status_value)
        total_pages = max(1, ceil(total / page_size)) if total > 0 else 1
        current_page = min(page, total_pages) if total > 0 else 1
        offset = (current_page - 1) * page_size

        parties = self.repository.list_parties(
            q=q,
            status=status_value,
            offset=offset,
            limit=page_size,
        )

        return {
            "items": parties,
            "page": current_page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    def suggest_parties(self, q: str | None = None, limit: int = 10) -> list[IndentingParty]:
        return self.repository.suggest_parties(q=q, limit=limit)

    def get_party(self, party_id: int) -> IndentingParty:
        party = self.repository.get_party(party_id)
        if party is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")
        return party

    def create_party(self, payload: IndentingPartyCreate, actor: User) -> IndentingParty:
        return self.repository.create_party(
            name=payload.name,
            contact_person=payload.contact_person,
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
            city=payload.city,
            country=payload.country,
            tax_id=payload.tax_id,
            notes=payload.notes,
            status=IndentingPartyStatus.ACTIVE,
            created_by=actor.id,
        )

    def update_party(self, party_id: int, payload: IndentingPartyUpdate) -> IndentingParty:
        party = self.get_party(party_id)
        update_data = payload.model_dump(exclude_unset=True)
        return self.repository.update_party(party, **update_data)

    def deactivate_party(self, party_id: int) -> IndentingParty:
        party = self.get_party(party_id)
        return self.repository.update_party(party, status=IndentingPartyStatus.INACTIVE)

    def activate_party(self, party_id: int) -> IndentingParty:
        party = self.get_party(party_id)
        return self.repository.update_party(party, status=IndentingPartyStatus.ACTIVE)

    # ─── Deals ─────────────────────────────────────────────────────────────────

    def list_deals(
        self,
        *,
        q: str | None = None,
        status_value: IndentingDealStatus | None = None,
        party_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        total = self.repository.count_deals(q=q, status=status_value, party_id=party_id)
        total_pages = max(1, ceil(total / page_size)) if total > 0 else 1
        current_page = min(page, total_pages) if total > 0 else 1
        offset = (current_page - 1) * page_size

        deals = self.repository.list_deals(
            q=q,
            status=status_value,
            party_id=party_id,
            offset=offset,
            limit=page_size,
        )

        return {
            "items": [self._enrich_deal(deal) for deal in deals],
            "page": current_page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    def get_deal(self, deal_id: int) -> dict[str, Any]:
        deal = self.repository.get_deal(deal_id)
        if deal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indenting deal not found")
        return self._enrich_deal(deal)

    def create_deal(self, payload: IndentingDealCreate, actor: User) -> dict[str, Any]:
        if payload.party_a_id == payload.party_b_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Party A and Party B must be different parties",
            )

        party_a = self.get_party(payload.party_a_id)
        party_b = self.get_party(payload.party_b_id)

        if party_a.status != IndentingPartyStatus.ACTIVE or party_b.status != IndentingPartyStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both parties must be active to create a deal",
            )

        # Calculate commission
        commission_amount = self._compute_commission_amount(
            deal_value=payload.deal_value,
            commission_type=payload.commission_type,
            rate=payload.commission_rate,
            fixed_amount=payload.commission_amount,
        )

        deal = self.repository.create_deal(
            party_a_id=payload.party_a_id,
            party_b_id=payload.party_b_id,
            product=payload.product,
            quantity=payload.quantity,
            unit=payload.unit,
            deal_value=payload.deal_value,
            currency=payload.currency.upper(),
            deal_date=payload.deal_date,
            status=IndentingDealStatus.OPEN,
            commission_type=payload.commission_type,
            commission_rate=payload.commission_rate,
            commission_amount=commission_amount,
            commission_currency=payload.commission_currency.upper(),
            commission_payer=payload.commission_payer,
            remarks=payload.remarks,
            created_by=actor.id,
        )

        return self._enrich_deal(deal)

    def update_deal(self, deal_id: int, payload: IndentingDealUpdate) -> dict[str, Any]:
        raw_deal = self.repository.get_deal(deal_id)
        if raw_deal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indenting deal not found")

        update_data = payload.model_dump(exclude_unset=True)

        party_a_id = update_data.get("party_a_id", raw_deal.party_a_id)
        party_b_id = update_data.get("party_b_id", raw_deal.party_b_id)

        if party_a_id == party_b_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Party A and Party B must be different parties",
            )

        # Recalculate commission if commission parameters changed
        deal_value = update_data.get("deal_value", raw_deal.deal_value)
        commission_type = update_data.get("commission_type", raw_deal.commission_type)
        commission_rate = update_data.get("commission_rate", raw_deal.commission_rate)
        commission_amount = update_data.get("commission_amount", raw_deal.commission_amount)

        if any(k in update_data for k in ("deal_value", "commission_type", "commission_rate", "commission_amount")):
            new_amount = self._compute_commission_amount(
                deal_value=deal_value,
                commission_type=commission_type,
                rate=commission_rate,
                fixed_amount=commission_amount,
            )
            update_data["commission_amount"] = new_amount

        if "currency" in update_data and update_data["currency"]:
            update_data["currency"] = update_data["currency"].upper()
        if "commission_currency" in update_data and update_data["commission_currency"]:
            update_data["commission_currency"] = update_data["commission_currency"].upper()

        updated_deal = self.repository.update_deal(raw_deal, **update_data)
        return self._enrich_deal(updated_deal)

    def update_deal_status(self, deal_id: int, new_status: IndentingDealStatus) -> dict[str, Any]:
        raw_deal = self.repository.get_deal(deal_id)
        if raw_deal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indenting deal not found")

        updated_deal = self.repository.update_deal(raw_deal, status=new_status)
        return self._enrich_deal(updated_deal)

    # ─── Payments ──────────────────────────────────────────────────────────────

    def add_payment(
        self,
        deal_id: int,
        payload: IndentingCommissionPaymentCreate,
        actor: User,
    ) -> dict[str, Any]:
        raw_deal = self.repository.get_deal(deal_id)
        if raw_deal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indenting deal not found")

        # Invariant: Payment currency must match deal's commission currency
        payment_currency = payload.currency.upper()
        if payment_currency != raw_deal.commission_currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment currency ({payment_currency}) must match deal commission currency ({raw_deal.commission_currency})",
            )

        self.repository.create_payment(
            deal_id=deal_id,
            amount=payload.amount,
            currency=payment_currency,
            payment_date=payload.payment_date,
            reference=payload.reference,
            notes=payload.notes,
            created_by=actor.id,
        )

        refreshed_deal = self.repository.get_deal(deal_id)
        return self._enrich_deal(refreshed_deal)

    def delete_payment(self, deal_id: int, payment_id: int) -> dict[str, Any]:
        payment = self.repository.get_payment(deal_id=deal_id, payment_id=payment_id)
        if payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        self.repository.delete_payment(payment)
        refreshed_deal = self.repository.get_deal(deal_id)
        return self._enrich_deal(refreshed_deal)

    # ─── Summary ───────────────────────────────────────────────────────────────

    def get_summary(self) -> IndentingSummaryResponse:
        deals = self.repository.get_all_deals_for_summary()
        active_parties = self.repository.count_active_parties()

        # Group solely by commission currency
        by_currency: dict[str, dict[str, Any]] = {}

        for deal in deals:
            curr = deal.commission_currency
            if curr not in by_currency:
                by_currency[curr] = {
                    "currency": curr,
                    "total_deal_value": Decimal(0),
                    "expected_commission": Decimal(0),
                    "received_commission": Decimal(0),
                    "pending_commission": Decimal(0),
                    "deal_count": 0,
                }

            total_paid = sum((p.amount for p in deal.payments), Decimal(0))
            pending = max(deal.commission_amount - total_paid, Decimal(0))

            by_currency[curr]["total_deal_value"] += deal.deal_value
            by_currency[curr]["expected_commission"] += deal.commission_amount
            by_currency[curr]["received_commission"] += total_paid
            by_currency[curr]["pending_commission"] += pending
            by_currency[curr]["deal_count"] += 1

        items = [CurrencySummaryItem(**data) for data in sorted(by_currency.values(), key=lambda x: x["currency"])]

        return IndentingSummaryResponse(
            currencies=items,
            total_deals=len(deals),
            active_parties=active_parties,
        )

    # ─── Helper Calculations ───────────────────────────────────────────────────

    def _compute_commission_amount(
        self,
        *,
        deal_value: Decimal,
        commission_type: IndentingCommissionType,
        rate: Decimal | None,
        fixed_amount: Decimal | None,
    ) -> Decimal:
        if commission_type == IndentingCommissionType.PERCENT:
            if rate is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Commission rate is required for percentage commission",
                )
            return round((deal_value * rate) / Decimal(100), 2)
        elif commission_type == IndentingCommissionType.FIXED:
            if fixed_amount is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Commission amount is required for fixed commission",
                )
            return fixed_amount
        return Decimal(0)

    def _enrich_deal(self, deal: IndentingDeal) -> dict[str, Any]:
        total_paid = sum((p.amount for p in deal.payments), Decimal(0))
        balance_due = max(deal.commission_amount - total_paid, Decimal(0))

        if total_paid == Decimal(0):
            payment_status = "pending"
        elif total_paid < deal.commission_amount:
            payment_status = "partial"
        elif total_paid == deal.commission_amount:
            payment_status = "paid"
        else:
            payment_status = "overpaid"

        deal_dict = {
            "id": deal.id,
            "reference": deal.reference,
            "party_a_id": deal.party_a_id,
            "party_b_id": deal.party_b_id,
            "party_a": deal.party_a,
            "party_b": deal.party_b,
            "product": deal.product,
            "quantity": deal.quantity,
            "unit": deal.unit,
            "deal_value": deal.deal_value,
            "currency": deal.currency,
            "deal_date": deal.deal_date,
            "status": deal.status,
            "commission_type": deal.commission_type,
            "commission_rate": deal.commission_rate,
            "commission_amount": deal.commission_amount,
            "commission_currency": deal.commission_currency,
            "commission_payer": deal.commission_payer,
            "remarks": deal.remarks,
            "created_by": deal.created_by,
            "created_at": deal.created_at,
            "updated_at": deal.updated_at,
            "payment_status": payment_status,
            "total_paid": total_paid,
            "balance_due": balance_due,
            "payments": deal.payments,
        }

        return IndentingDealRead.model_validate(deal_dict).model_dump(mode="json")
