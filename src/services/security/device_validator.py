import string
from dataclasses import dataclass

from apps.users.services.storage import IProfileService
from services.constructor.validators import BaseValidator
from services.security.exceptions import (
    InvalidDeviceToken,
    NotUniqueDeviceToken,
    UnauthorizedDevice,
)
from services.security.mobile_auth import MobileAuthorizationCredentials


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
        try:
            await self.repository.get_by_device(token)
        except TypeError:
            return
        else:
            raise NotUniqueDeviceToken()
