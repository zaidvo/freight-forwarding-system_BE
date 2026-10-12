from sqlalchemy.orm import Session

from app.modules.modules.model import Module


MODULE_SEED_DATA = [
    {
        "name": "Account Management",
        "slug": "account-management",
        "icon": "users",
        "color": "#3b82f6",
        "route": "/accounts",
        "is_active": True,
        "sort_order": 1,
    },
    {
        "name": "Operations",
        "slug": "operations",
        "icon": "ship",
        "color": "#0ea5e9",
        "route": None,
        "is_active": False,
        "sort_order": 2,
    },
    {
        "name": "Finance",
        "slug": "finance",
        "icon": "wallet",
        "color": "#059669",
        "route": None,
        "is_active": False,
        "sort_order": 3,
    },
    {
        "name": "Sales",
        "slug": "sales",
        "icon": "shopping-cart",
        "color": "#f59e0b",
        "route": None,
        "is_active": False,
        "sort_order": 4,
    },
    {
        "name": "Marketing",
        "slug": "marketing",
        "icon": "bar-chart-3",
        "color": "#c026d3",
        "route": None,
        "is_active": False,
        "sort_order": 5,
    },
    {
        "name": "Indenting",
        "slug": "indenting",
        "icon": "handshake",
        "color": "#f59e0b",
        "route": "/indenting",
        "is_active": True,
        "sort_order": 6,
    },
    {
        "name": "Customers",
        "slug": "customers",
        "icon": "building-2",
        "color": "#7c3aed",
        "route": "/customers",
        "is_active": True,
        "sort_order": 7,
    },
]


def seed_modules(db: Session) -> None:
    for entry in MODULE_SEED_DATA:
        existing = db.query(Module).filter(Module.slug == entry["slug"]).one_or_none()
        if existing:
            for key, value in entry.items():
                setattr(existing, key, value)
        else:
            db.add(Module(**entry))

    db.commit()
