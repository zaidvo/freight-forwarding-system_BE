from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.access.model import AccessGroup
from app.modules.access.repository import AccessRepository
from app.modules.users.model import UserRole


class AccessService:
    def __init__(self, db: Session):
        self.repository = AccessRepository(db)

    def list_groups(self) -> list[AccessGroup]:
        return self.repository.list_groups()

    def create_group(self, *, name: str, description: str | None, module_ids: list[int]) -> AccessGroup:
        modules = self._get_modules_or_400(module_ids)
        return self.repository.create_group(name=name, description=description, modules=modules)

    def update_group(
        self,
        *,
        group_id: int,
        name: str | None = None,
        description: str | None = None,
        module_ids: list[int] | None = None,
    ) -> AccessGroup:
        group = self._get_group_or_404(group_id)
        modules = self._get_modules_or_400(module_ids) if module_ids is not None else None
        return self.repository.update_group(group, name=name, description=description, modules=modules)

    def delete_group(self, group_id: int) -> None:
        group = self._get_group_or_404(group_id)
        self.repository.delete_group(group)

    def set_user_groups(self, *, user_id: int, group_ids: list[int]) -> None:
        user = self.repository.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.role == UserRole.ROOT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Root user groups cannot be changed")

        groups = [self._get_group_or_404(group_id) for group_id in group_ids]
        self.repository.set_user_groups(user, groups)

    def _get_group_or_404(self, group_id: int) -> AccessGroup:
        group = self.repository.get_group(group_id)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group

    def _get_modules_or_400(self, module_ids: list[int]) -> list:
        modules = self.repository.get_modules(module_ids)
        found_ids = {module.id for module in modules}
        missing_ids = sorted(set(module_ids) - found_ids)
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid module id(s): {', '.join(str(module_id) for module_id in missing_ids)}",
            )
        return modules
