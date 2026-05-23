from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.modules.model import Module
from app.modules.users.model import User, UserRole, UserStatus
from app.modules.users.repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")

    return user


def require_root(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ROOT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Root access required")

    return current_user


def require_module_access(module_slug: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.ROOT:
            return current_user

        has_access = any(
            module.slug == module_slug
            for group in current_user.groups
            for module in group.modules
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{module_slug} access required",
            )

        return current_user

    return dependency


def get_accessible_module_slugs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[str]:
    if current_user.role == UserRole.ROOT:
        return list(db.scalars(select(Module.slug).order_by(Module.sort_order)).all())

    slugs = {
        module.slug
        for group in current_user.groups
        for module in group.modules
    }
    return sorted(slugs)
