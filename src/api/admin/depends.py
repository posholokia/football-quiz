from loguru import logger

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from apps.users.exceptions.auth import InvalidToken
from apps.users.models import UserEntity
from apps.users.services.auth.jwt_auth.models import BlacklistRefreshToken
from apps.users.services.storage.base import IUserService
from apps.users.services.storage.sqla import ORMUserService
from config.containers import get_container
from services.jwt_token.exceptions import DecodeJWTError


async def get_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> UserEntity:
    """Возвращает user_id из payload в access токене"""
    token = credentials.credentials
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(
        BlacklistRefreshToken
    )
    repository: ORMUserService = container.resolve(IUserService)
    try:
        payload = token_service.decode(token)
        user_id = payload["user_id"]
        return await repository.get_by_id(user_id)
    except DecodeJWTError as e:
        logger.debug("Не удалось декодировать токен: {}", e)
        raise InvalidToken()
