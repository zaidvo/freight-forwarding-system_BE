from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.common.response import make_response
from app.db.session import get_db
from app.modules.audit.model import ActivityAction, ActivityLog
from app.modules.audit.schemas import ActivityLogRead
from app.modules.auth.dependencies import require_module_access
from app.modules.users.model import User


router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])
require_account_management = require_module_access("account-management")

AuditCategory = str


def _category_filters(category: AuditCategory | None):
    if category == "important":
        return [ActivityLog.action.notin_([ActivityAction.LOGIN, ActivityAction.LOGOUT])]
    if category == "account":
        return [
            ActivityLog.action.in_(
                [
                    ActivityAction.CREATE_USER,
                    ActivityAction.UPDATE_USER,
                    ActivityAction.DEACTIVATE_USER,
                ]
            )
        ]
    if category == "security":
        return [
            (ActivityLog.success.is_(False))
            | ActivityLog.action.in_(
                [
                    ActivityAction.FAILED_LOGIN,
                    ActivityAction.CHANGE_PASSWORD,
                    ActivityAction.FORGOT_PASSWORD,
                    ActivityAction.RESET_PASSWORD,
                ]
            )
        ]
    if category == "auth":
        return [
            ActivityLog.action.in_(
                [ActivityAction.LOGIN, ActivityAction.LOGOUT, ActivityAction.FAILED_LOGIN]
            )
        ]
    return []


@router.get("")
def list_activity_logs(
    db: Session = Depends(get_db),
    _: User = Depends(require_account_management),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    category: AuditCategory | None = Query(
        default="important", pattern="^(important|account|security|auth|all)$"
    ),
):
    filters = _category_filters(None if category == "all" else category)
    actor = aliased(User)
    target = aliased(User)
    total = db.scalar(select(func.count(ActivityLog.id)).where(*filters)) or 0
    total_pages = max(1, ceil(total / page_size))
    current_page = min(page, total_pages)
    offset = (current_page - 1) * page_size

    rows = db.execute(
        select(ActivityLog, actor, target)
        .outerjoin(actor, ActivityLog.actor_user_id == actor.id)
        .outerjoin(target, ActivityLog.target_user_id == target.id)
        .where(*filters)
        .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    items = [
        ActivityLogRead(
            id=log.id,
            actor_user_id=log.actor_user_id,
            actor_name=actor_user.full_name if actor_user else None,
            actor_email=actor_user.email if actor_user else None,
            action=log.action,
            target_user_id=log.target_user_id,
            target_name=target_user.full_name if target_user else None,
            target_email=target_user.email if target_user else None,
            success=log.success,
            description=log.description,
            ip_address=log.ip_address,
            created_at=log.created_at,
        ).model_dump(mode="json")
        for log, actor_user, target_user in rows
    ]

    return make_response(
        True,
        "Activity logs fetched successfully",
        {
            "items": items,
            "page": current_page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "category": category,
        },
    )
