from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ActivityAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DEACTIVATE_USER = "deactivate_user"
    CHANGE_PASSWORD = "change_password"
    FORGOT_PASSWORD = "forgot_password"
    RESET_PASSWORD = "reset_password"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action: Mapped[ActivityAction] = mapped_column(
        SQLAEnum(
            ActivityAction,
            name="activity_action_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
