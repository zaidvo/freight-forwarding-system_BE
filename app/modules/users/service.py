from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.audit.model import ActivityAction
from app.modules.audit.service import ActivityLogService
from app.modules.users.model import User, UserRole, UserStatus
from app.modules.users.repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.activity_logs = ActivityLogService(db)

    def list_users(self) -> list[User]:
        return self.repository.list()

    def get_user(self, user_id: int) -> User:
        return self._get_user_or_404(user_id)

    def create_user(
        self,
        *,
        full_name: str,
        email: str,
        password: str,
        role: UserRole,
        actor: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        if self.repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = self.repository.create(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            created_by=actor.id,
        )
        self.activity_logs.log(
            actor_user_id=actor.id,
            action=ActivityAction.CREATE_USER,
            target_user_id=user.id,
            success=True,
            description=f"Root created user {user.full_name}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return user

    def update_user(
        self,
        *,
        user_id: int,
        actor: User,
        full_name: str | None = None,
        email: str | None = None,
        role: UserRole | None = None,
        status_value: UserStatus | None = None,
        password: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        user = self._get_user_or_404(user_id)
        self._ensure_not_root(user)
        if email is not None:
            existing_user = self.repository.get_by_email(email)
            if existing_user and existing_user.id != user.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        updated_user = self.repository.update(
            user,
            full_name=full_name,
            email=email.lower() if email else None,
            role=role,
            status=status_value,
            password_hash=hash_password(password) if password else None,
        )
        self.activity_logs.log(
            actor_user_id=actor.id,
            action=ActivityAction.UPDATE_USER,
            target_user_id=user.id,
            success=True,
            description=f"Root updated user {updated_user.full_name}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return updated_user

    def deactivate_user(
        self,
        *,
        user_id: int,
        actor: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        user = self._get_user_or_404(user_id)
        self._ensure_not_root(user)
        updated_user = self.repository.set_status(user, UserStatus.INACTIVE)
        self.activity_logs.log(
            actor_user_id=actor.id,
            action=ActivityAction.DEACTIVATE_USER,
            target_user_id=user.id,
            success=True,
            description=f"Root deactivated user {updated_user.full_name}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return updated_user

    def activate_user(
        self,
        *,
        user_id: int,
        actor: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        user = self._get_user_or_404(user_id)
        self._ensure_not_root(user)
        updated_user = self.repository.set_status(user, UserStatus.ACTIVE)
        self.activity_logs.log(
            actor_user_id=actor.id,
            action=ActivityAction.UPDATE_USER,
            target_user_id=user.id,
            success=True,
            description=f"Root activated user {updated_user.full_name}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return updated_user

    def _get_user_or_404(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

    def _ensure_not_root(self, user: User) -> None:
        if user.role == UserRole.ROOT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Root user cannot be updated or deleted")
