from api.admin.auth.schema import (
    AuthCredentialsSchema,
    TokenObtainPairSchema,
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


@router.post("/jwt/create/", status_code=status.HTTP_200_OK)
async def login(
    credentials: AuthCredentialsSchema,
    container: Container = Depends(get_container),
) -> TokenObtainPairSchema:
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

    return TokenObtainPairSchema(
        access=access,
        refresh=refresh,
    )
