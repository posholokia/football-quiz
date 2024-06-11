from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.actions.mixins import ORMAlchemy
from services.storage_service.dto import GameSettingsDTO
from services.storage_service.game_settings_db.interface import ORMGameSettingsService


@dataclass
class GameSettingsActions(ORMAlchemy):
    session: AsyncSession
    storage: ORMGameSettingsService = ORMGameSettingsService

    async def get(self) -> GameSettingsDTO:
        async with self.session.begin():
            return await self.storage.get_game_settings()
