from dataclasses import dataclass

from core.apps.users.exceptions.profile import ProfileDoesNotMatchTheDevice
from core.apps.users.services.storage import IProfileService
from core.services.constructor.permissions import BasePermission
from core.services.security.exceptions import UnauthorizedDevice


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
