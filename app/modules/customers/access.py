from fastapi import Depends, HTTPException, status

from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import User, UserRole


def require_any_module_access(*module_slugs: str):
    allowed = set(module_slugs)

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.ROOT:
            return current_user

        user_modules = {
            module.slug
            for group in current_user.groups
            for module in group.modules
        }
        if not user_modules.intersection(allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these modules is required: {', '.join(module_slugs)}",
            )
        return current_user

    return dependency
