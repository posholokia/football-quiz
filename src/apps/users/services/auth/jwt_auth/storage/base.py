from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class ITokenStorage(ABC):
    @abstractmethod
    async def set_token(
        self, key: str, value: str, expire: int | float
    ) -> None:
        """
        Поместить токен в хранилище токенов.

        :param key:     Jti подпись токена.
        :param value:   Токен.
        :param expire:  Время истечения токена, timestamp метка.
        :return:        None.
        """

    @abstractmethod
    async def get_token(self, key: str) -> str | None:
        """
        Получить токен из хранилища.

        :param key: Jti подпись токена.
        :return:    Токен или None, если не найден.
        """
