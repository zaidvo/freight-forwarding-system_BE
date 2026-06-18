from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_module_access, require_root
from app.modules.users.model import User, UserRole
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["Users"])
require_account_management = require_module_access("account-management")


@router.get("")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_account_management)):
    users = UserService(db).list_users()
    data = [_serialize_user(user) for user in users]
    return make_response(True, "Users fetched successfully", data)


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_account_management)):
    user = UserService(db).get_user(user_id)
    return make_response(True, "User fetched successfully", _serialize_user(user))


@router.post("")
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_root),
):
    user = UserService(db).create_user(
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        role=UserRole.USER,
        actor=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User created successfully", _serialize_user(user))


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_root),
):
    user = UserService(db).update_user(
        user_id=user_id,
        actor=current_user,
        full_name=payload.full_name,
        email=payload.email,
        status_value=payload.status,
        password=payload.password,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User updated successfully", _serialize_user(user))


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_root),
):
    user = UserService(db).deactivate_user(
        user_id=user_id,
        actor=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User deactivated successfully", _serialize_user(user))


@router.patch("/{user_id}/activate")
def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_root),
):
    user = UserService(db).activate_user(
        user_id=user_id,
        actor=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User activated successfully", _serialize_user(user))


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client else None


def _serialize_user(user: User) -> dict:
    data = UserRead.model_validate(user).model_dump(mode="json")
    data["group_ids"] = [group.id for group in user.groups]
    return data
