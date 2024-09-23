from dataclasses import dataclass

from apps.users.exceptions.auth import (
    InvalidAuthCredentials,
    InvalidToken,
)
from apps.users.services.auth.jwt_auth.models import BlacklistRefreshToken
from apps.users.services.auth.pwd_hash import check_password
from apps.users.services.storage.base import IUserService
from services.jwt_token.exceptions import (
    DecodeJWTError,
    InvalidTokenType,
    TokenInBlacklistError,
)


@dataclass
class AuthAction:
    __repository: IUserService
    token_service: BlacklistRefreshToken

    async def login(self, username: str, password: str) -> tuple[str, str]:
        """
        Метод проверки пароля и логина пользователя. Если данные
        верные, возвращает access и refresh токены.

        :param username:    Юзернейм юзера.
        :param password:    Пароль юзера.
        :return:            Пару refresh и access токенов.
        """
        user = await self.__repository.get_one(username=username)

        if user is None or not check_password(password, user.password):
            raise InvalidAuthCredentials()

        refresh = await self.token_service.for_user(user)
        access = await self.token_service.access_token(refresh)
        return refresh, access

    async def refresh_token(self, token: str) -> str:
        """
        Метод обновления access токена по refresh токену.

        :param token:   Refresh токен.
        :return:        Access токен.
        """
        try:
            access = await self.token_service.access_token(token)
        except DecodeJWTError:
            raise InvalidToken(
                detail="Некорректный токен, ошибка при попытке декодировать"
            )
        except InvalidTokenType:
            raise InvalidToken(detail="Некорректный тип токена")
        except TokenInBlacklistError:
            raise InvalidToken(detail="Токен в черном списке")
        return access

    async def set_blacklist_token(self, token: str) -> None:
        """
        Заблокировать токен.

        :param token:   Refresh токен.
        :return:        None.
        """
        try:
            await self.token_service.set_blacklist(token)
        except DecodeJWTError:
            raise InvalidToken(
                detail="Некорректный токен, ошибка при попытке декодировать"
            )
        except InvalidTokenType:
            raise InvalidToken(detail="Некорректный тип токена")
