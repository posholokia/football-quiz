from api.admin.auth.schema import (
    AccessTokenSchema,
    AuthCredentialsSchema,
    RefreshTokenSchema,
    TokenObtainPairSchemaSchema,
)
from punq import Container

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.users.actions.user import AdminAuthAction
from apps.users.services.auth.jwt_auth.models import BlacklistRefreshToken
from config.containers import get_container


router = APIRouter()


@router.post(
    "/jwt/create/",
    status_code=status.HTTP_200_OK,
    description="Выдает пару токенов когда пользователь логинится",
)
async def login(
    credentials: AuthCredentialsSchema,
    container: Container = Depends(get_container),
) -> TokenObtainPairSchemaSchema:
    action: AdminAuthAction = container.resolve(AdminAuthAction)
    user = await action.login(
        username=credentials.username,
        password=credentials.password,
    )
    token_service: BlacklistRefreshToken = container.resolve(
        BlacklistRefreshToken
    )
    refresh = await token_service.for_user(user)
    access = await token_service.access_token(refresh)

    return TokenObtainPairSchemaSchema(
        access=access,
        refresh=refresh,
    )


@router.post(
    "/jwt/refresh/",
    status_code=status.HTTP_200_OK,
    description="Обновляет access токен по refresh токену",
)
async def refresh_token(
    token: RefreshTokenSchema,
    container: Container = Depends(get_container),
) -> AccessTokenSchema:
    token_service: BlacklistRefreshToken = container.resolve(
        BlacklistRefreshToken
    )
    access = await token_service.access_token(token.refresh)

    return AccessTokenSchema(
        access=access,
    )


@router.post(
    "/jwt/blacklist/",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Помещает refresh токен в черный список",
)
async def blacklist_token(
    token: RefreshTokenSchema,
    container: Container = Depends(get_container),
) -> None:
    token_service: BlacklistRefreshToken = container.resolve(
        BlacklistRefreshToken
    )
    await token_service.set_blacklist(token.refresh)

    return
