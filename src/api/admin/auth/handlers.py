from api.admin.auth.schema import (
    AccessTokenSchema,
    AuthCredentialsSchema,
    RefreshTokenSchema,
    TokenObtainPairSchemaSchema,
)

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.users.actions.user import AdminAuthAction
from config.containers import (
    Container,
    get_container,
)


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
    refresh, access = await action.login(
        username=credentials.username,
        password=credentials.password,
    )
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
    action: AdminAuthAction = container.resolve(AdminAuthAction)
    access = await action.refresh_token(token.refresh)
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
    action: AdminAuthAction = container.resolve(AdminAuthAction)
    await action.set_blacklist_token(token.refresh)
    return
