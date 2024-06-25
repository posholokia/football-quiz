from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.game_settings.models import GameSettings
from services.storage_service.base import IGameSettingsService
from services.storage_service.dto import GameSettingsDTO
from services.storage_service.game_settings_db.converter import game_settings_orm_to_dto


@dataclass
class ORMGameSettingsService(IGameSettingsService):
    session: AsyncSession

    async def get_game_settings(self) -> GameSettingsDTO:
        query = select(GameSettings).limit(1)
        result = await self.session.execute(query)
        orm_result = result.scalars().first()
        return await game_settings_orm_to_dto(orm_result)
