import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.indenting.model import (
    IndentingCommissionPayment,
    IndentingDeal,
    IndentingParty,
    IndentingPartyStatus,
)


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    return " ".join(cleaned.split())


class IndentingRepository:
    def __init__(self, db: Session):
        self.db = db

    # ─── Parties ───────────────────────────────────────────────────────────────

    def list_parties(
        self,
        *,
        q: str | None = None,
        status: IndentingPartyStatus | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[IndentingParty]:
        stmt = select(IndentingParty)
        conditions = []

        if status:
            conditions.append(IndentingParty.status == status)

        if q and q.strip():
            query_term = f"%{q.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(IndentingParty.name).like(query_term),
                    func.lower(IndentingParty.code).like(query_term),
                    func.lower(IndentingParty.contact_person).like(query_term),
                    func.lower(IndentingParty.email).like(query_term),
                    func.lower(IndentingParty.phone).like(query_term),
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.order_by(IndentingParty.created_at.desc(), IndentingParty.id.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count_parties(
        self,
        *,
        q: str | None = None,
        status: IndentingPartyStatus | None = None,
    ) -> int:
        stmt = select(func.count(IndentingParty.id))
        conditions = []

        if status:
            conditions.append(IndentingParty.status == status)

        if q and q.strip():
            query_term = f"%{q.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(IndentingParty.name).like(query_term),
                    func.lower(IndentingParty.code).like(query_term),
                    func.lower(IndentingParty.contact_person).like(query_term),
                    func.lower(IndentingParty.email).like(query_term),
                    func.lower(IndentingParty.phone).like(query_term),
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        return self.db.scalar(stmt) or 0

    def suggest_parties(self, q: str | None = None, limit: int = 10) -> list[IndentingParty]:
        stmt = select(IndentingParty).where(IndentingParty.status == IndentingPartyStatus.ACTIVE)
        if q and q.strip():
            query_term = f"%{q.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(IndentingParty.name).like(query_term),
                    func.lower(IndentingParty.code).like(query_term),
                    func.lower(IndentingParty.contact_person).like(query_term),
                )
            )
        stmt = stmt.order_by(IndentingParty.name.asc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_party(self, party_id: int) -> IndentingParty | None:
        return self.db.get(IndentingParty, party_id)

    def party_has_deals(self, party_id: int) -> bool:
        stmt = select(func.count(IndentingDeal.id)).where(
            or_(IndentingDeal.party_a_id == party_id, IndentingDeal.party_b_id == party_id)
        )
        count = self.db.scalar(stmt) or 0
        return count > 0

    def generate_party_code(self) -> str:
        stmt = select(func.max(IndentingParty.id))
        max_id = self.db.scalar(stmt) or 0
        return f"PAR-{(max_id + 1):05d}"

    def create_party(self, **values) -> IndentingParty:
        if not values.get("code"):
            values["code"] = self.generate_party_code()
        if "name" in values and "normalized_name" not in values:
            values["normalized_name"] = normalize_text(values["name"])

        party = IndentingParty(**values)
        self.db.add(party)
        self.db.commit()
        self.db.refresh(party)
        return party

    def update_party(self, party: IndentingParty, **values) -> IndentingParty:
        for key, value in values.items():
            if value is not None:
                setattr(party, key, value)
        if "name" in values and values["name"] is not None:
            party.normalized_name = normalize_text(values["name"])

        party.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(party)
        return party

    # ─── Deals ─────────────────────────────────────────────────────────────────

    def list_deals(
        self,
        *,
        q: str | None = None,
        status: Any = None,
        party_id: int | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[IndentingDeal]:
        stmt = (
            select(IndentingDeal)
            .options(
                selectinload(IndentingDeal.party_a),
                selectinload(IndentingDeal.party_b),
                selectinload(IndentingDeal.payments),
            )
        )
        conditions = []

        if status:
            conditions.append(IndentingDeal.status == status)

        if party_id:
            conditions.append(or_(IndentingDeal.party_a_id == party_id, IndentingDeal.party_b_id == party_id))

        if q and q.strip():
            query_term = f"%{q.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(IndentingDeal.reference).like(query_term),
                    func.lower(IndentingDeal.product).like(query_term),
                    func.lower(IndentingDeal.remarks).like(query_term),
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.order_by(IndentingDeal.created_at.desc(), IndentingDeal.id.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count_deals(
        self,
        *,
        q: str | None = None,
        status: Any = None,
        party_id: int | None = None,
    ) -> int:
        stmt = select(func.count(IndentingDeal.id))
        conditions = []

        if status:
            conditions.append(IndentingDeal.status == status)

        if party_id:
            conditions.append(or_(IndentingDeal.party_a_id == party_id, IndentingDeal.party_b_id == party_id))

        if q and q.strip():
            query_term = f"%{q.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(IndentingDeal.reference).like(query_term),
                    func.lower(IndentingDeal.product).like(query_term),
                    func.lower(IndentingDeal.remarks).like(query_term),
                )
            )

        if conditions:
            stmt = stmt.where(*conditions)

        return self.db.scalar(stmt) or 0

    def get_deal(self, deal_id: int) -> IndentingDeal | None:
        stmt = (
            select(IndentingDeal)
            .where(IndentingDeal.id == deal_id)
            .options(
                selectinload(IndentingDeal.party_a),
                selectinload(IndentingDeal.party_b),
                selectinload(IndentingDeal.payments),
            )
        )
        return self.db.scalar(stmt)

    def generate_deal_reference(self) -> str:
        stmt = select(func.max(IndentingDeal.id))
        max_id = self.db.scalar(stmt) or 0
        return f"IND-{(max_id + 1):05d}"

    def create_deal(self, **values) -> IndentingDeal:
        if not values.get("reference"):
            values["reference"] = self.generate_deal_reference()

        deal = IndentingDeal(**values)
        self.db.add(deal)
        self.db.commit()
        return self.get_deal(deal.id)  # Returns with relationships loaded

    def update_deal(self, deal: IndentingDeal, **values) -> IndentingDeal:
        for key, value in values.items():
            if value is not None:
                setattr(deal, key, value)
        deal.updated_at = datetime.utcnow()
        self.db.commit()
        return self.get_deal(deal.id)

    # ─── Payments ──────────────────────────────────────────────────────────────

    def create_payment(self, **values) -> IndentingCommissionPayment:
        payment = IndentingCommissionPayment(**values)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, deal_id: int, payment_id: int) -> IndentingCommissionPayment | None:
        stmt = select(IndentingCommissionPayment).where(
            IndentingCommissionPayment.deal_id == deal_id,
            IndentingCommissionPayment.id == payment_id,
        )
        return self.db.scalar(stmt)

    def delete_payment(self, payment: IndentingCommissionPayment) -> None:
        self.db.delete(payment)
        self.db.commit()

    # ─── Summary ───────────────────────────────────────────────────────────────

    def get_all_deals_for_summary(self) -> list[IndentingDeal]:
        stmt = select(IndentingDeal).options(selectinload(IndentingDeal.payments))
        return list(self.db.scalars(stmt).all())

    def count_active_parties(self) -> int:
        stmt = select(func.count(IndentingParty.id)).where(IndentingParty.status == IndentingPartyStatus.ACTIVE)
        return self.db.scalar(stmt) or 0
