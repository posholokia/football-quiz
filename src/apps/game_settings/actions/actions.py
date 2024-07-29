from dataclasses import dataclass

from apps.game_settings.dto.dto import GameSettingsDTO
from apps.game_settings.services.storage.base import IGameSettingsService


@dataclass
class GameSettingsActions:
    repository: IGameSettingsService

    async def get(self) -> GameSettingsDTO:
        return await self.repository.get()
