from api.admin.depends import is_admin_permission
from api.admin.game_settings.schema import (
    GameSettingsAdminSchema,
    GameSettingsUpdateSchema,
)

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer
from starlette import status

from apps.game_settings.actions import GameSettingsActions
from config.containers import (
    Container,
    get_container,
)
from services.mapper import dataclass_to_schema


router = APIRouter()
http_bearer = HTTPBearer()


@router.get(
    "/admin/settings/",
    status_code=status.HTTP_200_OK,
    description="Получить настройки игры",
)
async def get_game_settings(
    _=Depends(is_admin_permission),
    container: Container = Depends(get_container),
) -> GameSettingsAdminSchema:
    action: GameSettingsActions = container.resolve(GameSettingsActions)
    settings = await action.get_settings()
    return dataclass_to_schema(GameSettingsAdminSchema, settings)


@router.patch(
    "/admin/settings/",
    status_code=status.HTTP_200_OK,
    description="Обновить настройки игры",
)
async def patch_game_settings(
    settings: GameSettingsUpdateSchema,
    _=Depends(is_admin_permission),
    container: Container = Depends(get_container),
) -> GameSettingsAdminSchema:
    action: GameSettingsActions = container.resolve(GameSettingsActions)
    settings = await action.edit_settings(
        **{
            field: getattr(settings, field)
            for field in settings.model_fields.keys()
            if getattr(settings, field) is not None
        }
    )
    return dataclass_to_schema(GameSettingsAdminSchema, settings)
