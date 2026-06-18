from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.access.model import AccessGroup
from app.modules.modules.model import Module
from app.modules.users.model import User


class AccessRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_groups(self) -> list[AccessGroup]:
        statement = (
            select(AccessGroup)
            .options(selectinload(AccessGroup.modules), selectinload(AccessGroup.users))
            .order_by(AccessGroup.id)
        )
        return list(self.db.scalars(statement).all())

    def get_group(self, group_id: int) -> AccessGroup | None:
        statement = (
            select(AccessGroup)
            .where(AccessGroup.id == group_id)
            .options(selectinload(AccessGroup.modules), selectinload(AccessGroup.users))
        )
        return self.db.scalar(statement)

    def get_modules(self, module_ids: list[int]) -> list[Module]:
        if not module_ids:
            return []

        statement = select(Module).where(Module.id.in_(module_ids))
        return list(self.db.scalars(statement).all())

    def create_group(self, *, name: str, description: str | None, modules: list[Module]) -> AccessGroup:
        group = AccessGroup(name=name, description=description, modules=modules)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return self.get_group(group.id) or group

    def update_group(
        self,
        group: AccessGroup,
        *,
        name: str | None = None,
        description: str | None = None,
        modules: list[Module] | None = None,
    ) -> AccessGroup:
        if name is not None:
            group.name = name
        if description is not None:
            group.description = description
        if modules is not None:
            group.modules.clear()
            self.db.flush()
            group.modules = modules

        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return self.get_group(group.id) or group

    def delete_group(self, group: AccessGroup) -> None:
        self.db.delete(group)
        self.db.commit()

    def get_user(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id).options(selectinload(User.groups))
        return self.db.scalar(statement)

    def set_user_groups(self, user: User, groups: list[AccessGroup]) -> User:
        user.groups = groups
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
