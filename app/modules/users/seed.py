from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.users.model import UserRole
from app.modules.users.repository import UserRepository


def seed_super_admin(db: Session, *, full_name: str, email: str, password: str):
    repository = UserRepository(db)
    existing_user = repository.get_by_email(email)
    if existing_user is not None:
        return existing_user

    return repository.create(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.SUPER_ADMIN,
        created_by=None,
    )
