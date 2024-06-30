import string
from abc import abstractmethod, ABC
from dataclasses import dataclass

from core.apps.users.services.storage.base import IProfileService
from core.services.security.exceptions import InvalidDeviceToken, UnauthorizedDevice, NotUniqueDeviceToken
from core.services.security.mobile_auth import MobileAuthorizationCredentials
from core.services.constructor.validators import BaseValidator


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
        if type(token) is not str:
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
