from dataclasses import dataclass
from datetime import timedelta

from apps.users.models import UserEntity
from apps.users.services.auth.jwt_auth.storage.base import ITokenStorage
from services.jwt_token.exceptions import (
    InvalidTokenType,
    TokenInBlacklistError,
)
from services.jwt_token.models import (
    Token,
    TokenType,
)


@dataclass
class AccessToken(Token):
    token_type: TokenType = TokenType.access
    lifetime: timedelta = timedelta(minutes=5)


@dataclass
class RefreshToken(Token):
    token_type: TokenType = TokenType.refresh
    lifetime: timedelta = timedelta(weeks=2)
    sub_claim: str = "user"

    async def access_token(self, refresh_token: str) -> str:
        """
        Обновление access токена.

        :param refresh_token:   Refresh токен.
        :return:                Access токен.
        """
        payload = self.decode(refresh_token)

        # проверяем что access токен обновляется по refresh токену
        if payload["typ"] != self.token_type.value:
            raise InvalidTokenType("Неверный тип refresh токена")

        access_token_cls = AccessToken()
        access_token_cls.set_payload()
        access_token_cls[self.sub_claim] = payload[self.sub_claim]
        access = access_token_cls.encode()
        return access

    async def for_user(self, user: UserEntity) -> str:
        """
        Выдаем refresh токен юзеру.

        :param user:    Юзер.
        :return:        Refresh токен.
        """
        self.set_payload()
        self[self.sub_claim] = {
            "id": user.id,
            "superuser": user.is_superuser,
            "active": user.is_active,
        }
        return self.encode()


@dataclass
class BlacklistRefreshToken(RefreshToken):
    """
    Refresh токен добавляется в черный список.
    Черный список хранится в хранилище, при выдаче нового access
    токена проверяем что его нет в черном списке, тогда
    выдаем токен. Бан осуществляется по подписи токена jti - uuid4.
    :param storage: Хранилище забаненных токенов.
    """

    def __init__(self, storage: ITokenStorage):
        super().__init__()
        self.storage = storage

    async def access_token(self, refresh_token: str) -> str:
        """
        Обновление access токена. Перед обновлением проверяется,
        что refresh токен не заблокирован.

        :param refresh_token:   Refresh токен.
        :return:                Access токен.
        """
        await self.check_blacklist(refresh_token)
        return await super().access_token(refresh_token)

    async def set_blacklist(self, token: str) -> None:
        """
        Записываем токен в хранилище в черный список.

        :param token:   Jwt токен.
        :return:        None.
        """
        payload = self.decode(token)
        key = payload["jti"]
        timestamp_exp = payload["exp"]
        await self.storage.set_token(
            key=key,
            value=token,
            expire=timestamp_exp,
        )

    async def check_blacklist(self, token: str) -> None:
        """
        Проверяем, что токена нет в черном списке.
        Если есть, поднимаем ошибку.

        :param token:   Jwt токен.
        :return:        None.
        """
        payload = self.decode(token)
        value = await self.storage.get_token(payload["jti"])

        if value is not None:
            raise TokenInBlacklistError("Токен в черном списке")
