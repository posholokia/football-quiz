from dataclasses import dataclass

from core.apps.users.services.storage.base import IProfileService
from core.services.constructor.permissions import BasePermission
from core.services.security.exceptions import UnauthorizedDevice


@dataclass(frozen=True, eq=False)
class DevicePermissions(BasePermission):
    repository: IProfileService

    async def has_permission(self, token: str) -> None:
        try:
            await self.repository.get_by_device(token)
        except TypeError:
            raise UnauthorizedDevice()
