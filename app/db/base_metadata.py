from app.db.base import Base


# Import all models so Alembic autogenerate can discover them.
from app.modules.access.model import AccessGroup, GroupModule, UserGroup  # noqa: E402,F401
from app.modules.audit.model import ActivityLog  # noqa: E402,F401
from app.modules.auth.model import PasswordResetToken  # noqa: E402,F401
from app.modules.indenting.model import (  # noqa: E402,F401
    IndentingCommissionPayment,
    IndentingDeal,
    IndentingParty,
)
from app.modules.modules.model import Module  # noqa: E402,F401
from app.modules.trading_import.model import (  # noqa: E402,F401
    TradingSalesDetentionInvoice,
    TradingSalesDocument,
    TradingSalesForm,
    TradingSalesFreightInvoice,
    TradingSalesImportRecord,
    TradingSalesPaymentReceipt,
)
from app.modules.users.model import User  # noqa: E402,F401