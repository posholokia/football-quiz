from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from core.api.mobile.depends import get_auth_credentials
from core.apps.game_settings.actions import GameSettingsActions
from core.apps.game_settings.schema import GameSettingsSchema
from core.apps.quiz.permissions.quiz import DevicePermissions
from core.config.containers import get_container
from core.services.security.mobile_auth import MobileAuthorizationCredentials

router = APIRouter()


@router.get("/game_settings/", status_code=status.HTTP_200_OK)
async def get_game_settings(
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> GameSettingsSchema:
    """Получение настроек игры"""
    container = get_container()
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    actions: GameSettingsActions = container.resolve(GameSettingsActions)
    game_settings = await actions.get()
    return GameSettingsSchema.from_dto(game_settings)
