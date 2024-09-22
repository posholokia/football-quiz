import string
from dataclasses import dataclass

from apps.users.services.storage import IProfileService
from core.constructor.validators import BaseValidator
from core.security.fingerprint_auth.exceptions import (
    InvalidDeviceToken,
    NotUniqueDeviceToken,
    UnauthorizedDevice,
)
from core.security.fingerprint_auth.mobile_auth import (
    MobileAuthorizationCredentials,
)


@dataclass
class DeviceTokenValidate(BaseValidator):
    repository: IProfileService

    async def validate(self, cred: MobileAuthorizationCredentials) -> None:
        if cred.type == "device":
            await self._check_token_type(cred.token)
            await self._token_not_exists(cred.token)
            return
        raise UnauthorizedDevice()

    @staticmethod
    async def _check_token_type(token: str) -> None:
        if not isinstance(token, str):
            raise InvalidDeviceToken()
        allow_symbols = f"{string.ascii_lowercase}{string.digits}"
        if (len(token) != 32) or (
            not all(char in allow_symbols for char in token)
        ):
            raise InvalidDeviceToken()

    async def _token_not_exists(self, token) -> None:
        if await self.repository.exists(device_uuid=token):
            raise NotUniqueDeviceToken()
