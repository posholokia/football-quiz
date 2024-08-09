from dataclasses import dataclass
from typing import (
    Generic,
    Type,
    TypeVar,
)

from sqlalchemy import (
    and_,
    delete,
    desc,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

from apps.users.exceptions.statistics import StatisticDoseNotExists
from apps.users.models import (
    Profile,
    Statistic,
)
from apps.users.services.storage import IStatisticService
from core.database.db import (
    Base,
    Database,
)


TModel = TypeVar("TModel", bound=Base)


@dataclass
class ORMStatisticService(IStatisticService, Generic[TModel]):
    db: Database
    model: Type[TModel]

    async def create(self, pk: int, place: int) -> Statistic:
        async with self.db.get_session() as session:
            return await self._sub_create(session, pk, place)

    async def get_by_profile(self, profile_pk: int) -> Statistic:
        async with self.db.get_ro_session() as session:
            stat = await self._sub_get_by_profile(session, profile_pk)

            if stat is None:
                raise StatisticDoseNotExists(
                    detail=f"Статистика для игрока с id: {profile_pk} не найдена"
                )
            return stat

    async def get_by_place(self, place: int) -> Statistic | None:
        async with self.db.get_ro_session() as session:
            query = select(self.model).where(self.model.place == place)
            res = await session.execute(query)
            orm_result = res.scalar()

            if orm_result is None:
                return None
            return orm_result

    async def get_or_create_by_profile(self, profile_pk: int) -> Statistic:
        async with self.db.get_session() as session:
            # пытаемся получить статистику
            statistic = await self._sub_get_by_profile(session, profile_pk)

            if statistic is None:  # если не найдена
                # вычисляем последнее место
                place = await self._sub_get_count(session)
                # добавляем статистику на последнее место
                statistic = await self._sub_create(
                    session, profile_pk, place + 1
                )

            return statistic

    async def replace_profiles(self, new_place, old_place) -> None:
        """
        Смещение игроков в ладдере,
        когда юзер перемещается на новое место
        """
        async with self.db.get_session() as session:
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
            await session.commit()

    async def down_place_negative_score(self) -> None:
        """
        Смещение на 1 позицию вниз в рейтинге
        игроков с отрицательными очками
        """
        async with self.db.get_session() as session:
            query = (
                update(self.model)
                .where(self.model.score < 0)
                .values(
                    place=self.model.place + 1,
                    trend=self.model.trend - 1,
                )
            )
            await session.execute(query)

    async def patch(self, pk: int, **fields) -> Statistic:
        async with self.db.get_session() as session:
            query = (
                update(self.model)
                .where(self.model.id == pk)
                .values(**fields)
                .returning(self.model)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalar()

    async def get_user_rank(
        self,
        profile_pk: int,
    ) -> int:
        """Положение юзера в ладдере на основе его статистики"""
        async with self.db.get_ro_session() as session:
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
    ) -> list[Statistic]:
        """Получение топа игроков"""
        async with self.db.get_ro_session() as session:
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
            result = await session.execute(query)
            return result.scalars().all()

    async def get_count(self) -> int:
        """Общее количество игроков со статистикой"""
        async with self.db.get_ro_session() as session:
            return await self._sub_get_count(session)

    async def get_count_positive_score(self) -> int:
        """Количество игроков с не отрицательными очками"""
        async with self.db.get_ro_session() as session:
            query = (
                select(func.count())
                .select_from(self.model)
                .where(self.model.score >= 0)
            )
            result = await session.execute(query)
            return result.scalar_one()

    async def clear_statistic(self) -> None:
        """Обнуление данных в таблице"""
        async with self.db.get_session() as session:
            assert (
                self.model is not Statistic
            ), "Попытка обнулить общую статистику"

            if self.model is Statistic:
                return

            query = update(self.model).values(
                games=0,
                score=0,
                rights=0,
                wrongs=0,
                trend=0,
            )
            await session.execute(query)
            await session.flush()

            query = select(self.model).order_by(self.model.profile_id)
            res = await session.execute(query)
            statistics = res.scalars().all()

            for idx, stat in enumerate(statistics, start=1):
                query = (
                    update(self.model)
                    .where(self.model.id == stat.id)
                    .values(place=idx)
                )
                await session.execute(query)

            await session.commit()

    async def delete_all_statistics(self) -> None:
        """Удаление всех данных из таблицы"""
        async with self.db.get_session() as session:
            assert (
                self.model is not Statistic
            ), "Попытка удалить общую статистику"

            if self.model is Statistic:
                return

            query = delete(self.model)
            await session.execute(query)
            await session.commit()

    async def _sub_create(
        self,
        session: AsyncSession,
        pk: int,
        place: int,
    ) -> Statistic:
        """Вспомогательная функция создания объекта"""
        statistic = self.model(
            profile_id=pk,
            place=place,
        )
        session.add(statistic)
        await session.commit()
        return statistic

    async def _sub_get_count(self, session: AsyncSession) -> int:
        """Вспомогательная функция подсчета объектов"""
        query = select(func.count(self.model.id))
        result = await session.execute(query)
        return result.scalar_one()

    async def _sub_get_by_profile(
        self,
        session: AsyncSession,
        profile_pk: int,
    ) -> Statistic | None:
        """Вспомогательная функция получения объекта"""
        query = (
            select(self.model)
            .join(self.model.profile)
            .outerjoin(Profile.title)
            .options(joinedload(self.model.profile).joinedload(Profile.title))
            .where(self.model.profile_id == profile_pk)
        )
        res = await session.execute(query)
        orm_result = res.scalar()

        if orm_result is None:
            return None

        return orm_result


if __name__ == "__main__":
    import asyncio

    from apps.users.services.storage.base import IStatisticService
    from config.containers import get_container

    async def main():
        container = get_container()
        repo: ORMStatisticService = container.resolve(IStatisticService)
        res = await repo.get_top_gamers(0, 10)

        for i in res:
            print(i.to_entity())

    asyncio.run(main())
