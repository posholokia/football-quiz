from dataclasses import dataclass

from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.exc import (
    IntegrityError,
    NoResultFound,
)

from apps.users.models import BestPlayerTitle
from apps.users.services.storage.base import IProfileTitleService
from core.database.db import Database


@dataclass
class ORMProfileTitleService(IProfileTitleService):
    db: Database

    async def get_or_create_by_profile(
        self,
        profile_pk: int,
    ) -> BestPlayerTitle:
        async with self.db.get_session() as session:
            try:
                query = select(BestPlayerTitle).where(
                    BestPlayerTitle.profile_id == profile_pk
                )
                res = await session.execute(query)
                return res.one()[0]
            except NoResultFound:
                title = BestPlayerTitle(
                    best_of_the_day=0,
                    best_of_the_month=0,
                    profile_id=profile_pk,
                )
                try:
                    session.add(title)
                    await session.flush()
                    return title
                except IntegrityError:
                    await session.rollback()
                    query = select(BestPlayerTitle).where(
                        BestPlayerTitle.profile_id == profile_pk
                    )
                    res = await session.execute(query)
                    return res.one()[0]

    async def patch(self, profile_pk: int, **fields) -> BestPlayerTitle:
        async with self.db.get_session() as session:
            query = (
                update(BestPlayerTitle)
                .where(BestPlayerTitle.profile_id == profile_pk)
                .values(**fields)
                .returning(BestPlayerTitle)
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
