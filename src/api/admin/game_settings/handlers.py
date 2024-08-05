from api.admin.depends import get_user_from_token
from api.admin.game_settings.schema import (
    GameSettingsAdminSchema,
    GameSettingsUpdateSchema,
)
from punq import Container

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer
from starlette import status

from apps.game_settings.actions.admin import AdminGameSettingsActions
from apps.users.models import UserEntity
from apps.users.permissions.admin import IsAdminUser
from config.containers import get_container
from services.mapper import Mapper


router = APIRouter()
http_bearer = HTTPBearer()


@router.get(
    "/admin/settings/",
    status_code=status.HTTP_200_OK,
    description="Получить настройки игры",
)
async def get_game_settings(
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> GameSettingsAdminSchema:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: AdminGameSettingsActions = container.resolve(
        AdminGameSettingsActions
    )
    settings = await action.get()
    return Mapper.dataclass_to_schema(GameSettingsAdminSchema, settings)


@router.patch(
    "/admin/settings/",
    status_code=status.HTTP_200_OK,
    description="Обновить настройки игры",
)
async def patch_game_settings(
    settings: GameSettingsUpdateSchema,
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> GameSettingsAdminSchema:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: AdminGameSettingsActions = container.resolve(
        AdminGameSettingsActions
    )
    settings = await action.patch(
        **{
            field: getattr(settings, field)
            for field in settings.__fields__.keys()
            if getattr(settings, field) is not None
        }
    )
    return Mapper.dataclass_to_schema(GameSettingsAdminSchema, settings)
