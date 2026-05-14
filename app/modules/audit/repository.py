from sqlalchemy.orm import Session

from app.modules.audit.model import ActivityAction, ActivityLog


class ActivityLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
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
        log = ActivityLog(
            actor_user_id=actor_user_id,
            action=action,
            target_user_id=target_user_id,
            success=success,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
