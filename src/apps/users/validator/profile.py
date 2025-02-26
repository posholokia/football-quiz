from dataclasses import dataclass

import aiohttp

from apps.users.exceptions.profile import (
    InvalidProfileName,
    ProfanityServiceNotAvailable,
    ProfileNameIsProfanity,
)
from core.constructor.validators import BaseValidator


TIMEOUT = aiohttp.ClientTimeout(total=2)


@dataclass
class ProfileValidator(BaseValidator):
    async def validate(self, name: str | None = None) -> None:
        """
        Валидация имени пользователя.

        :param name:    Имя профиля.
        :return:        Ничего не возвращает, поднимает ошибку
                        если валидация не пройдена.
        """
        if name is not None:
            await self._profile_name_validate(name)

    @staticmethod
    async def _profile_name_validate(name: str) -> None:
        if len(name) > 50:
            raise InvalidProfileName()

        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                async with session.post(
                    f"http://profanity:8000/censor-word/{name}"  # noqa: E231
                ) as response:
                    res = await response.text()
                    if res == "true":
                        raise ProfileNameIsProfanity()
        except TimeoutError:
            raise ProfanityServiceNotAvailable()


@dataclass
class ProfileValidatorLocal(BaseValidator):
    async def validate(self, name: str | None = None) -> None:
        if name is not None:
            if len(name) > 50:
                raise InvalidProfileName()
