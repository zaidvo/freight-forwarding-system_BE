from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_password_reset_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.audit.model import ActivityAction
from app.modules.audit.service import ActivityLogService
from app.modules.auth.repository import PasswordResetTokenRepository
from app.modules.users.model import User, UserStatus
from app.modules.users.repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.reset_tokens = PasswordResetTokenRepository(db)
        self.activity_logs = ActivityLogService(db)

    def login(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str]:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            self.activity_logs.log(
                action=ActivityAction.FAILED_LOGIN,
                success=False,
                description=f"Failed login attempt for {email.lower()}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            self.activity_logs.log(
                action=ActivityAction.FAILED_LOGIN,
                success=False,
                target_user_id=user.id,
                description=f"Inactive user login attempt for {email.lower()}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

        self.users.update(user, last_login_at=datetime.now(timezone.utc))
        token = create_access_token(str(user.id))
        self.activity_logs.log(
            actor_user_id=user.id,
            action=ActivityAction.LOGIN,
            target_user_id=user.id,
            success=True,
            description=f"User {user.email} logged in",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return user, token

    def logout(
        self,
        *,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        self.activity_logs.log(
            actor_user_id=user.id,
            action=ActivityAction.LOGOUT,
            target_user_id=user.id,
            success=True,
            description=f"User {user.email} logged out",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def forgot_password(
        self,
        *,
        email: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str | None:
        user = self.users.get_by_email(email)
        if user is None:
            self.activity_logs.log(
                action=ActivityAction.FORGOT_PASSWORD,
                success=False,
                description=f"Forgot password requested for unknown email {email.lower()}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            return None

        reset_token = create_password_reset_token()
        self.reset_tokens.create(
            user_id=user.id,
            token_hash=hash_token(reset_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        self.activity_logs.log(
            actor_user_id=user.id,
            action=ActivityAction.FORGOT_PASSWORD,
            target_user_id=user.id,
            success=True,
            description=f"Forgot password requested for {user.email}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return reset_token

    def reset_password(
        self,
        *,
        token: str,
        new_password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        now = datetime.now(timezone.utc)
        reset_token = self.reset_tokens.get_active_by_hash(hash_token(token), now)
        if reset_token is None:
            self.activity_logs.log(
                action=ActivityAction.RESET_PASSWORD,
                success=False,
                description="Invalid or expired password reset token",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

        user = self.users.get_by_id(reset_token.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        self.users.update(user, password_hash=hash_password(new_password))
        self.reset_tokens.mark_used(reset_token, now)
        self.activity_logs.log(
            actor_user_id=user.id,
            action=ActivityAction.RESET_PASSWORD,
            target_user_id=user.id,
            success=True,
            description=f"Password reset for {user.email}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return user

    def change_password(
        self,
        *,
        user: User,
        current_password: str,
        new_password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        if not verify_password(current_password, user.password_hash):
            self.activity_logs.log(
                actor_user_id=user.id,
                action=ActivityAction.CHANGE_PASSWORD,
                target_user_id=user.id,
                success=False,
                description=f"Failed password change for {user.email}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        updated_user = self.users.update(user, password_hash=hash_password(new_password))
        self.activity_logs.log(
            actor_user_id=user.id,
            action=ActivityAction.CHANGE_PASSWORD,
            target_user_id=user.id,
            success=True,
            description=f"Password changed for {user.email}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return updated_user
