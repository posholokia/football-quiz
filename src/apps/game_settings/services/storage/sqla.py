from dataclasses import dataclass

from sqlalchemy import (
    select,
    update,
)

from apps.game_settings.models import GameSettings
from apps.game_settings.services.storage.base import IGameSettingsService
from core.database.db import Database


@dataclass
class ORMGameSettingsService(IGameSettingsService):
    db: Database

    async def get(self) -> GameSettings:
        async with self.db.get_ro_session() as session:
            query = select(GameSettings).limit(1)
            result = await session.execute(query)
            return result.scalars().first()

    async def patch(self, **fields) -> GameSettings:
        """
        В БД может быть только одна запись с настройками,
        поэтому запрос без указания какой объект обновить.
        """
        async with self.db.get_session() as session:
            query = (
                update(GameSettings).values(**fields).returning(GameSettings)
            )
            result = await session.execute(query)
            orm_result = result.scalar()
            return orm_result


if __name__ == "__main__":
    import asyncio

    from apps.game_settings.services.storage.base import IGameSettingsService
    from config.containers import get_container

    async def main():
        container = get_container()
        repo: ORMGameSettingsService = container.resolve(IGameSettingsService)
        res = await repo.patch(question_limit=10)
        print(res.to_entity())

    asyncio.run(main())
