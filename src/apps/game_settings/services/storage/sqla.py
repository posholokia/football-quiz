from dataclasses import dataclass

from sqlalchemy import (
    select,
    update,
)

from apps.game_settings.converter import orm_game_settings_to_entity
from apps.game_settings.models import (
    GameSettings,
    GameSettingsEntity,
)
from apps.game_settings.services.storage.base import IGameSettingsService
from core.database.db import Database


@dataclass
class ORMGameSettingsService(IGameSettingsService):
    db: Database

    async def get(self) -> GameSettingsEntity:
        async with self.db.get_ro_session() as session:
            query = select(GameSettings).limit(1)
            result = await session.execute(query)
            orm_result = result.scalars().first()
            return await orm_game_settings_to_entity(orm_result)

    async def patch(self, **fields) -> GameSettingsEntity:
        """
        В БД может быть только одна запись с настройками,
        поэтому запрос без указания какой объект обновить.
        """
        async with self.db.get_session() as session:
            query = (
                update(GameSettings).values(**fields).returning(GameSettings)
            )
            result = await session.execute(query)
            orm_result = result.fetchone()
            return await orm_game_settings_to_entity(orm_result[0])
