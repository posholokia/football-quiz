from dataclasses import dataclass

from apps.game_settings.models import GameSettingsEntity
from apps.game_settings.services.storage.base import IGameSettingsService


@dataclass
class GameSettingsActions:
    repository: IGameSettingsService

    async def get(self) -> GameSettingsEntity:
        game_settings = await self.repository.get()
        return game_settings.to_entity()

    async def patch(self, **fields) -> GameSettingsEntity:
        game_settings = await self.repository.patch(**fields)
        return game_settings.to_entity()
