from dataclasses import dataclass

from apps.users.exceptions.profile import ProfileDoesNotMatchTheDevice
from apps.users.services.storage import IProfileService
from services.constructor.permissions import BasePermission
from services.security.exceptions import UnauthorizedDevice


@dataclass(frozen=True, eq=False)
class ProfilePermissions(BasePermission):
    repository: IProfileService

    async def has_permission(self, profile_pk: int, token: str) -> None:
        try:
            profile = await self.repository.get_by_device(token)
            if profile.id != profile_pk:
                raise ProfileDoesNotMatchTheDevice()
        except TypeError:
            raise UnauthorizedDevice()