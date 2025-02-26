from dataclasses import dataclass

from apps.users.services.storage import IProfileService
from core.constructor.permissions import BasePermission
from core.security.fingerprint_auth.exceptions import UnauthorizedDevice


@dataclass(frozen=True, eq=False)
class DevicePermissions(BasePermission):
    repository: IProfileService

    async def has_permission(self, token: str) -> None:
        if not await self.repository.exists(device_uuid=token):
            raise UnauthorizedDevice()
