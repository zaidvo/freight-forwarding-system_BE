from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.modules.customers.model import Customer, CustomerRole, CustomerRoleLink, CustomerStatus


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_customers(
        self,
        *,
        query_text: str | None,
        role: CustomerRole | None,
        status: CustomerStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Customer], int]:
        filters = []
        if query_text:
            term = f"%{query_text.strip()}%"
            filters.append(
                or_(
                    Customer.name.ilike(term),
                    Customer.code.ilike(term),
                    Customer.normalized_name.ilike(term),
                    Customer.email.ilike(term),
                    Customer.city.ilike(term),
                )
            )
        if role:
            filters.append(
                Customer.id.in_(
                    select(CustomerRoleLink.customer_id).where(CustomerRoleLink.role == role)
                )
            )
        if status:
            filters.append(Customer.status == status)

        base = select(Customer).where(*filters)
        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        items = self.db.scalars(
            base.options(joinedload(Customer.role_links))
            .order_by(Customer.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).unique().all()
        return items, total

    def suggest(self, *, query_text: str, limit: int = 10) -> list[Customer]:
        term = f"%{query_text.strip()}%"
        return self.db.scalars(
            select(Customer)
            .where(
                Customer.status == CustomerStatus.ACTIVE,
                or_(
                    Customer.name.ilike(term),
                    Customer.code.ilike(term),
                    Customer.normalized_name.ilike(term),
                    Customer.email.ilike(term),
                ),
            )
            .options(joinedload(Customer.role_links))
            .order_by(Customer.name.asc())
            .limit(limit)
        ).unique().all()

    def get(self, customer_id: int) -> Customer | None:
        return self.db.scalars(
            select(Customer)
            .where(Customer.id == customer_id)
            .options(joinedload(Customer.role_links))
        ).unique().first()

    def find_duplicates(self, *, normalized_name: str, customer_id: int | None) -> list[Customer]:
        query = select(Customer).where(Customer.normalized_name == normalized_name)
        if customer_id is not None:
            query = query.where(Customer.id != customer_id)
        return self.db.scalars(
            query.options(joinedload(Customer.role_links)).order_by(Customer.name.asc())
        ).unique().all()

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.flush()
        customer.code = f"CUS-{customer.id:05d}"
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def save(self, customer: Customer) -> Customer:
        self.db.commit()
        self.db.refresh(customer)
        return customer
