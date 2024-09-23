import pytest

from apps.users.models import UserEntity
from apps.users.services.auth.jwt_auth.models import BlacklistRefreshToken
from config.containers import get_container


@pytest.fixture(scope="function")
async def jwt_refresh_token():
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(BlacklistRefreshToken)
    return await token_service.for_user(
        UserEntity(
            id=2,
            password="secret",
            is_superuser=False,
            is_active=True,
            username="user",
        )
    )


@pytest.fixture(scope="function")
async def jwt_access_token(jwt_refresh_token):
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(BlacklistRefreshToken)
    refresh = await jwt_refresh_token
    return await token_service.access_token(refresh)


@pytest.fixture(scope="function")
async def jwt_refresh_admin_token():
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(BlacklistRefreshToken)
    return await token_service.for_user(
        UserEntity(
            id=1,
            password="super secret",
            is_superuser=True,
            is_active=True,
            username="admin",
        )
    )


@pytest.fixture(scope="function")
async def jwt_access_admin_token(jwt_refresh_admin_token):
    container = get_container()
    token_service: BlacklistRefreshToken = container.resolve(BlacklistRefreshToken)
    refresh = await jwt_refresh_admin_token
    return await token_service.access_token(refresh)
