from sqlalchemy.orm import Session

from app.modules.audit.model import ActivityAction, ActivityLog
from app.modules.audit.repository import ActivityLogRepository


class ActivityLogService:
    def __init__(self, db: Session):
        self.repository = ActivityLogRepository(db)

    def log(
        self,
        *,
        action: ActivityAction,
        success: bool,
        actor_user_id: int | None = None,
        target_user_id: int | None = None,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ActivityLog:
        return self.repository.create(
            action=action,
            success=success,
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
