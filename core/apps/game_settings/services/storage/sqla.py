from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.apps.game_settings.dto.converter import game_settings_orm_to_dto
from core.apps.game_settings.dto.dto import GameSettingsDTO
from core.apps.game_settings.models import GameSettings
from core.apps.game_settings.services.storage.base import IGameSettingsService


@dataclass
class ORMGameSettingsService(IGameSettingsService):
    session: AsyncSession

    async def get(self) -> GameSettingsDTO:
        async with self.session.begin():
            query = select(GameSettings).limit(1)
            result = await self.session.execute(query)
            orm_result = result.scalars().first()
            return await game_settings_orm_to_dto(orm_result)
