from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.access.schemas import GroupCreate, GroupRead, GroupUpdate, UserGroupsUpdate
from app.modules.access.service import AccessService
from app.modules.auth.dependencies import require_root
from app.modules.users.model import User


router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("")
def list_groups(db: Session = Depends(get_db), _: User = Depends(require_root)):
    groups = AccessService(db).list_groups()
    return make_response(True, "Groups fetched successfully", [_serialize_group(group) for group in groups])


@router.post("")
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    group = AccessService(db).create_group(
        name=payload.name,
        description=payload.description,
        module_ids=payload.module_ids,
    )
    return make_response(True, "Group created successfully", _serialize_group(group))


@router.put("/{group_id}")
def update_group(
    group_id: int,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    group = AccessService(db).update_group(
        group_id=group_id,
        name=payload.name,
        description=payload.description,
        module_ids=payload.module_ids,
    )
    return make_response(True, "Group updated successfully", _serialize_group(group))


@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db), _: User = Depends(require_root)):
    AccessService(db).delete_group(group_id)
    return make_response(True, "Group deleted successfully")


@router.put("/users/{user_id}")
def update_user_groups(
    user_id: int,
    payload: UserGroupsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_root),
):
    AccessService(db).set_user_groups(user_id=user_id, group_ids=payload.group_ids)
    return make_response(True, "User groups updated successfully")


def _serialize_group(group) -> dict:
    data = GroupRead(
        id=group.id,
        name=group.name,
        description=group.description,
        module_ids=[module.id for module in group.modules],
        user_ids=[user.id for user in group.users],
        created_at=group.created_at,
        updated_at=group.updated_at,
    )
    return data.model_dump(mode="json")
