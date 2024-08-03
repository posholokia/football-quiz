from dataclasses import dataclass

from sqlalchemy import select

from apps.game_settings.dto.converter import game_settings_orm_to_dto
from apps.game_settings.dto.dto import GameSettingsDTO
from apps.game_settings.models import GameSettings
from apps.game_settings.services.storage.base import IGameSettingsService
from core.database.db import Database


@dataclass
class ORMGameSettingsService(IGameSettingsService):
    db: Database

    async def get(self) -> GameSettingsDTO:
        async with self.db.get_session() as session:
            query = select(GameSettings).limit(1)
            result = await session.execute(query)
            orm_result = result.scalars().first()
            return await game_settings_orm_to_dto(orm_result)
