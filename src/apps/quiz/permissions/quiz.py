from dataclasses import dataclass

from apps.users.services.storage import IProfileService
from services.constructor.permissions import BasePermission
from services.security.exceptions import UnauthorizedDevice


@dataclass(frozen=True, eq=False)
class DevicePermissions(BasePermission):
    repository: IProfileService

    async def has_permission(self, token: str) -> None:
        try:
            await self.repository.get_by_device(token)
        except TypeError:
            raise UnauthorizedDevice()
