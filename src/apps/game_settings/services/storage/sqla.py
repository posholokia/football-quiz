from dataclasses import dataclass
from typing import Type

from sqlalchemy import (
    select,
    update,
)

from apps.game_settings.models import GameSettingsEntity
from apps.game_settings.services.storage.base import IGameSettingsService
from apps.users.services.storage import TModel
from core.database.db import Database
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMGameSettingsService(CommonRepository, IGameSettingsService):
    db: Database
    model: Type[TModel]

    async def get_one(self) -> GameSettingsEntity:
        async with self.db.get_ro_session() as session:
            query = select(self.model).limit(1)
            orm_result = await session.execute(query)
            gs = orm_result.scalars().first()
            return gs.to_entity()

    async def update(self, **fields) -> GameSettingsEntity:
        async with self.db.get_session() as session:
            query = update(self.model).values(**fields).returning(self.model)
            result = await session.execute(query)
            orm_result = result.scalar()
            return orm_result.to_entity()


if __name__ == "__main__":
    import asyncio

    from apps.game_settings.services.storage.base import IGameSettingsService
    from config.containers import get_container

    async def main():
        container = get_container()
        repo: ORMGameSettingsService = container.resolve(IGameSettingsService)
        await repo.update(question_limit=10)

    asyncio.run(main())
