from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.model import PasswordResetToken


class PasswordResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, user_id: int, token_hash: str, expires_at: datetime) -> PasswordResetToken:
        token = PasswordResetToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_active_by_hash(self, token_hash: str, now: datetime) -> PasswordResetToken | None:
        statement = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        return self.db.scalar(statement)

    def mark_used(self, token: PasswordResetToken, used_at: datetime) -> PasswordResetToken:
        token.used_at = used_at
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token
