from dataclasses import dataclass

from apps.game_settings.models import GameSettingsEntity
from apps.game_settings.services.storage.base import IGameSettingsService


@dataclass
class GameSettingsActions:
    repository: IGameSettingsService

    async def get(self) -> GameSettingsEntity:
        return await self.repository.get()

    async def patch(self, **fields) -> GameSettingsEntity:
        return await self.repository.patch(**fields)
