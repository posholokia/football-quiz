from dataclasses import dataclass
from typing import Generic

from sqlalchemy import (
    and_,
    delete,
    desc,
    select,
    update,
)
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

from apps.users.exceptions.statistics import StatisticDoseNotExists
from apps.users.models import (
    Profile,
    Statistic,
    StatisticEntity,
)
from apps.users.services.storage import (
    IStatisticService,
    TModel,
)
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMStatisticService(
    CommonRepository, IStatisticService, Generic[TModel]
):
    async def replace_profiles(self, new_place, old_place) -> None:
        async with self._db.get_session() as session:
            if new_place > old_place:
                query = (
                    update(self.model)
                    .where(
                        and_(
                            self.model.place <= new_place,
                            self.model.place > old_place,
                        )
                    )
                    .values(
                        place=self.model.place - 1,
                        trend=self.model.trend + 1,
                    )
                )
            else:
                query = (
                    update(self.model)
                    .where(
                        and_(
                            self.model.place >= new_place,
                            self.model.place < old_place,
                        )
                    )
                    .values(
                        place=self.model.place + 1,
                        trend=self.model.trend - 1,
                    )
                )
            await session.execute(query)

    async def down_place_negative_score(self) -> None:
        async with self._db.get_session() as session:
            query = (
                update(self.model)
                .where(self.model.score < 0)
                .values(
                    place=self.model.place + 1,
                    trend=self.model.trend - 1,
                )
            )
            await session.execute(query)

    async def get_user_rank(self, profile_pk: int) -> int:
        async with self._db.get_ro_session() as session:
            subquery = select(
                self.model,
                func.row_number()
                .over(
                    order_by=[
                        desc(self.model.score),
                        desc(self.model.games),
                        self.model.profile_id,
                    ]
                )
                .label("rank"),
            ).subquery()
            query = select(subquery.c.rank).where(
                subquery.c.profile_id == profile_pk
            )

            result = await session.execute(query)
            rank = result.fetchone()

            if rank is None:
                raise StatisticDoseNotExists()
            return rank[0]

    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[StatisticEntity]:
        async with self._db.get_ro_session() as session:
            query = (
                select(self.model)
                .order_by(self.model.place)
                .join(self.model.profile)
                .outerjoin(Profile.title)
                .options(
                    joinedload(self.model.profile).joinedload(Profile.title)
                )
                .offset(offset)
                .limit(limit)
            )
            orm_result = await session.execute(query)
            statistics = orm_result.scalars().all()
            return [s.to_entity() for s in statistics]

    async def get_count_positive_score(self) -> int:
        async with self._db.get_ro_session() as session:
            query = (
                select(func.count())
                .select_from(self.model)
                .where(self.model.score >= 0)
            )
            result = await session.execute(query)
            return result.scalar_one()

    async def delete_all_statistics(self) -> None:
        async with self._db.get_session() as session:
            assert (
                self.model is not Statistic
            ), "Попытка удалить общую статистику"

            if self.model is Statistic:
                return

            query = delete(self.model)
            await session.execute(query)

    async def get_profile_id(self, place: int) -> int | None:
        async with self._db.get_ro_session() as session:
            query = select(self.model.profile_id).where(
                self.model.place == place
            )
            res = await session.execute(query)
            return res.scalar()


if __name__ == "__main__":
    import asyncio

    from apps.users.services.storage.base import (
        IStatisticService,
        TModel,
    )
    from config.containers import get_container

    async def main():
        container = get_container()
        repo: IStatisticService = container.resolve(
            IStatisticService[Statistic]
        )
        # res = await repo.get_top_gamers(0, 10)
        res = await repo.get_user_rank(29)
        print(res)

    asyncio.run(main())
