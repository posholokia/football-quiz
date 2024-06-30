from dataclasses import dataclass
from core.services.constructor.validators import BaseValidator
from core.apps.users.exceptions.profile import InvalidProfile


@dataclass
class ProfileValidator(BaseValidator):
    async def validate(
            self,
            name: str | None = None,
    ) -> None:
        if name is not None:
            await self._profile_name_validate(name)

    @staticmethod
    async def _profile_name_validate(name: str) -> None:
        if len(name) > 50:
            raise InvalidProfile()
