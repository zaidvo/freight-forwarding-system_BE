from datetime import datetime

from pydantic import BaseModel

from app.modules.audit.model import ActivityAction


class ActivityLogRead(BaseModel):
    id: int
    actor_user_id: int | None
    actor_name: str | None
    actor_email: str | None
    action: ActivityAction
    target_user_id: int | None
    target_name: str | None
    target_email: str | None
    success: bool
    description: str | None
    ip_address: str | None
    created_at: datetime
