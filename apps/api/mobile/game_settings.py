from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.api.actions.game_settings import GameSettingsActions
from apps.game_settings.schema import GameSettings
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import check_device_profile_exists

from .depends import get_auth_credentials


router = APIRouter()


@router.get("/game_settings/", status_code=status.HTTP_200_OK)
async def get_game_settings(
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> GameSettings:
    """Получение настроек игры"""
    await check_device_profile_exists(cred)
    crud = await GameSettingsActions.start_session()
    game_settings = await crud.get()
    return game_settings
