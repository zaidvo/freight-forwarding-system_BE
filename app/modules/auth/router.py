from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import get_accessible_module_slugs, get_current_user
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
)
from app.modules.auth.service import AuthService
from app.modules.users.model import User
from app.modules.users.schemas import UserRead


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user, access_token = AuthService(db).login(
        email=payload.email,
        password=payload.password,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    data = LoginResponse(access_token=access_token, user=UserRead.model_validate(user))
    return make_response(True, "Login successful", data.model_dump(mode="json"))


@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    AuthService(db).logout(
        user=current_user,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "Logout successful")


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    reset_token = AuthService(db).forgot_password(
        email=payload.email,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    data = ForgotPasswordResponse(reset_token=reset_token)
    return make_response(True, "If the email exists, a reset token has been created", data.model_dump())


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    AuthService(db).reset_password(
        token=payload.token,
        new_password=payload.new_password,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "Password reset successful")


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    AuthService(db).change_password(
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
        ip_address=_client_host(request),
        user_agent=request.headers.get("user-agent"),
    )
    return make_response(True, "Password changed successfully")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return make_response(True, "Current user fetched", UserRead.model_validate(current_user).model_dump(mode="json"))


@router.get("/me/access")
def me_access(module_slugs: list[str] = Depends(get_accessible_module_slugs)):
    return make_response(True, "Current user access fetched", {"modules": module_slugs})


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client else None
