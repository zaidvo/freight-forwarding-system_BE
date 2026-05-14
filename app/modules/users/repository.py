from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.users.model import User, UserRole, UserStatus


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return self.db.scalar(statement)

    def list(self) -> list[User]:
        statement = select(User).order_by(User.id)
        return list(self.db.scalars(statement).all())

    def create(
        self,
        *,
        full_name: str,
        email: str,
        password_hash: str,
        role: UserRole,
        created_by: int | None,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email.lower(),
            password_hash=password_hash,
            role=role,
            status=UserStatus.ACTIVE,
            created_by=created_by,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **values) -> User:
        for key, value in values.items():
            if value is not None:
                setattr(user, key, value)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_status(self, user: User, status: UserStatus) -> User:
        user.status = status
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
