from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_super_admin
from app.modules.users.model import User
from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    users = UserService(db).list_users()
    data = [UserRead.model_validate(user).model_dump(mode="json") for user in users]
    return make_response(True, "Users fetched successfully", data)


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    user = UserService(db).get_user(user_id)
    return make_response(True, "User fetched successfully", UserRead.model_validate(user).model_dump(mode="json"))


@router.post("")
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = UserService(db).create_user(
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        actor=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User created successfully", UserRead.model_validate(user).model_dump(mode="json"))


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = UserService(db).update_user(
        user_id=user_id,
        actor=current_user,
        full_name=payload.full_name,
        email=payload.email,
        role=payload.role,
        status_value=payload.status,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User updated successfully", UserRead.model_validate(user).model_dump(mode="json"))


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = UserService(db).deactivate_user(
        user_id=user_id,
        actor=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User deactivated successfully", UserRead.model_validate(user).model_dump(mode="json"))


@router.patch("/{user_id}/activate")
def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = UserService(db).activate_user(
        user_id=user_id,
        actor=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "User activated successfully", UserRead.model_validate(user).model_dump(mode="json"))


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client else None
