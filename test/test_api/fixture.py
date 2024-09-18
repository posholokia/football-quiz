import pytest

from apps.users.models import UserEntity
from apps.users.services.auth.jwt_auth.models import BlacklistRefreshToken
from config.containers import get_container
from services.redis_pool import RedisPool


@pytest.fixture(scope="function")
async def jwt_refresh_token():
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(BlacklistRefreshToken)
    return await token_service.for_user(
        UserEntity(
            id=1,
            password="Здесь не важно",
            is_superuser=True,
            is_active=True,
            username="Здесь не важно",
        )
    )


@pytest.fixture(scope="function")
async def jwt_access_token(jwt_refresh_token):
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(BlacklistRefreshToken)
    refresh = await jwt_refresh_token
    return await token_service.access_token(refresh)
