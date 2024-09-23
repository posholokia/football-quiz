from dataclasses import dataclass

from sqlalchemy import update

from apps.users.models import BestPlayerTitleEntity
from apps.users.services.storage.base import IProfileTitleService
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMProfileTitleService(CommonRepository, IProfileTitleService):
    async def get_one(self, **filter_by) -> BestPlayerTitleEntity:
        result = await super().get_one(**filter_by)
        if result is None:
            return BestPlayerTitleEntity()
        return result

    async def update(self, profile_id: int, **fields) -> BestPlayerTitleEntity:
        async with self._db.get_session() as session:
            query = (
                update(self.model)
                .where(self.model.profile_id == profile_id)
                .values(**fields)
                .returning(self.model)
            )
            result = await session.execute(query)
            return result.scalar()


if __name__ == "__main__":
    import asyncio

    from apps.users.services.storage.base import IProfileTitleService
    from config.containers import get_container

    async def main():
        container = get_container()

        repo = container.resolve(IProfileTitleService)
        task1 = repo.get_or_create_by_profile(6407)
        task2 = repo.get_or_create_by_profile(6407)

        await asyncio.gather(task1, task2)

    asyncio.run(main())
