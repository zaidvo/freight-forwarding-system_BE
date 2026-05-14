from app.db.base import Base


# Import all models so Alembic autogenerate can discover them.
from app.modules.audit.model import ActivityLog  # noqa: E402,F401
from app.modules.auth.model import PasswordResetToken  # noqa: E402,F401
from app.modules.users.model import User  # noqa: E402,F401
