from dataclasses import dataclass

from apps.users.exceptions.auth import UserIsNotAdminError
from apps.users.models import UserEntity
from apps.users.services.storage.base import IUserService
from core.constructor.permissions import BasePermission


@dataclass(frozen=True, eq=False)
class IsAdminUser(BasePermission):
    repository: IUserService

    async def has_permission(self, user: UserEntity) -> None:
        print(user)
        if not user.is_superuser:
            raise UserIsNotAdminError()
