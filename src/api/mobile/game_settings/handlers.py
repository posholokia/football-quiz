from punq import Container

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.game_settings.actions import GameSettingsActions
from apps.quiz.permissions.quiz import DevicePermissions
from config.containers import get_container
from services.mapper import Mapper
from services.security.mobile_auth import (
    http_device,
    MobileAuthorizationCredentials,
)

from .schema import GameSettingsSchema


router = APIRouter()


@router.get("/game_settings/", status_code=status.HTTP_200_OK)
async def get_game_settings(
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> GameSettingsSchema:
    """Получение настроек игры"""
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    actions: GameSettingsActions = container.resolve(GameSettingsActions)
    game_settings = await actions.get()
    return Mapper.dataclass_to_schema(GameSettingsSchema, game_settings)
