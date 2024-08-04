from dataclasses import dataclass

from apps.users.exceptions.auth import InvalidAuthCredentials
from apps.users.models import UserEntity
from apps.users.permissions.admin import IsAdminUser
from apps.users.services.auth.pwd_hash import check_password
from apps.users.services.storage.base import IUserService


@dataclass
class AdminAuthAction:
    repository: IUserService
    permission: IsAdminUser

    async def login(self, username: str, password: str) -> UserEntity:
        user = await self.repository.get_by_username(username)

        if any(
            (
                user is None,
                not check_password(password, user.password),
            )
        ):
            raise InvalidAuthCredentials()
        await self.permission.has_permission(user)
        return user
