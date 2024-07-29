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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

from apps.users.dto import (
    ProfileDTO,
    StatisticDTO,
)
from apps.users.dto.converter import (
    orm_ladder_to_dto,
    orm_profile_title_to_dto,
    orm_profile_to_dto,
    orm_statistics_to_dto,
)
from apps.users.dto.dto import (
    LadderStatisticDTO,
    ProfileTitleDTO,
)
from apps.users.exceptions.profile import (
    AlreadyExistsProfile,
    DoesNotExistsProfile,
)
from apps.users.exceptions.statistics import StatisticDoseNotExists
from apps.users.models import (
    BestPlayerTitle,
    Profile,
    Statistic,
)
from apps.users.services.storage import (
    IProfileService,
    IStatisticService,
)
from apps.users.services.storage.base import IProfileTitleService
from config.database.db import Base


T = TypeVar("T", bound=Base)
D = TypeVar("D", bound=Base)
M = TypeVar("M", bound=Base)


@dataclass
class ORMProfileService(IProfileService):
    session: AsyncSession

    async def create(self, device: str) -> ProfileDTO:
        try:
            async with self.session.begin():
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device,
                )
                self.session.add(new_profile)
                await self.session.commit()
                return await orm_profile_to_dto(new_profile)

        except IntegrityError:
            raise AlreadyExistsProfile()

    async def get_or_create(self, device: str) -> ProfileDTO:
        async with self.session.begin():
            query = select(Profile).where(Profile.device_uuid == device)
            result = await self.session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device,
                )
                self.session.add(new_profile)
                await self.session.commit()
            else:
                new_profile = orm_result[0]
            return await orm_profile_to_dto(new_profile)

    async def patch(self, pk: int, **kwargs) -> ProfileDTO:
        async with self.session.begin():
            query = (
                update(Profile)
                .where(Profile.id == pk)
                .values(**kwargs)
                .returning(Profile)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            orm_result = result.fetchone()
            return await orm_profile_to_dto(orm_result[0])

    async def get_by_id(self, pk: int) -> ProfileDTO:
        async with self.session.begin():
            query = select(Profile).where(Profile.id == pk)
            result = await self.session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise DoesNotExistsProfile()

            return await orm_profile_to_dto(orm_result[0])

    async def get_by_device(self, token: str) -> ProfileDTO:
        async with self.session.begin():
            query = select(Profile).where(Profile.device_uuid == token)
            result = await self.session.execute(query)
            orm_result = result.fetchone()
            return await orm_profile_to_dto(orm_result[0])


@dataclass
class ORMStatisticService(IStatisticService, Generic[T]):
    session: AsyncSession
    model: Type[T]

    async def create(self, pk: int, place: int) -> StatisticDTO:
        async with self.session.begin():
            stat = await self._sub_create(pk, place)
            return await orm_statistics_to_dto(stat)

    async def get_by_profile(self, profile_pk: int) -> StatisticDTO:
        async with self.session.begin():
            stat = await self._sub_get_by_profile(profile_pk)

            if stat is None:
                raise StatisticDoseNotExists(
                    detail=f"Статистика для игрока с id: {profile_pk} не найдена"
                )
            return await orm_statistics_to_dto(stat)

    async def get_by_place(self, place: int) -> StatisticDTO | None:
        async with self.session.begin():
            query = select(self.model).where(self.model.place == place)
            res = await self.session.execute(query)
            orm_result = res.fetchone()

            if orm_result is None:
                return None
            return await orm_statistics_to_dto(orm_result[0])

    async def get_or_create_by_profile(self, profile_pk: int) -> StatisticDTO:
        async with self.session.begin():
            # пытаемся получить статистику
            statistic = await self._sub_get_by_profile(profile_pk)

            if statistic is None:  # если не найдена
                # вычисляем последнее место
                place = await self._sub_get_count()
                # добавляем статистику на последнее место
                statistic = await self._sub_create(profile_pk, place + 1)

            return await orm_statistics_to_dto(statistic)

    async def replace_profiles(self, new_place, old_place) -> None:
        """
        Смещение игроков в ладдере,
        когда юзер перемещается на новое место
        """
        async with self.session.begin():
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
            await self.session.execute(query)
            await self.session.commit()

    async def down_place_negative_score(self) -> None:
        """
        Смещение на 1 позицию вниз в рейтинге
        игроков с отрицательными очками
        """
        async with self.session.begin():
            query = (
                update(self.model)
                .where(self.model.score < 0)
                .values(
                    place=self.model.place + 1,
                    trend=self.model.trend - 1,
                )
            )
            await self.session.execute(query)

    async def patch(self, pk: int, **fields) -> StatisticDTO:
        async with self.session.begin():
            query = (
                update(self.model)
                .where(self.model.id == pk)
                .values(**fields)
                .returning(self.model)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            orm_result = result.fetchone()
            return await orm_statistics_to_dto(orm_result[0])

    async def get_user_rank(
        self,
        profile_pk: int,
    ) -> int:
        """Положение юзера в ладдере на основе его статистики"""
        async with self.session.begin():
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

            result = await self.session.execute(query)
            rank = result.fetchone()

            if rank is None:
                raise StatisticDoseNotExists()
            return rank[0]

    # async def get_top_gamers(
    #     self,
    #     offset: int | None,
    #     limit: int | None,
    # ) -> list[LadderStatisticDTO]:
    #     """Получение топа игроков"""
    #     async with self.session.begin():
    #         query = (
    #             select(self.model)
    #             .order_by(self.model.place)
    #             .offset(offset)
    #             .limit(limit)
    #             .options(selectinload(self.model.profile))
    #         )
    #         result = await self.session.execute(query)
    #         ladder = result.scalars().all()
    #         return [await orm_ladder_to_dto(obj) for obj in ladder]

    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[LadderStatisticDTO]:
        """Получение топа игроков"""
        async with self.session.begin():
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
            result = await self.session.execute(query)
            ladder = result.scalars().all()
            return [await orm_ladder_to_dto(obj) for obj in ladder]

    async def get_count(self) -> int:
        """Общее количество игроков со статистикой"""
        async with self.session.begin():
            return await self._sub_get_count()

    async def get_count_positive_score(self) -> int:
        """Количество игроков с не отрицательными очками"""
        async with self.session.begin():
            query = (
                select(func.count())
                .select_from(self.model)
                .where(self.model.score >= 0)
            )
            result = await self.session.execute(query)
            return result.scalar_one()

    async def clear_statistic(self) -> None:
        """Обнуление данных в таблице"""
        async with self.session.begin():
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
            await self.session.execute(query)
            await self.session.flush()

            query = select(self.model).order_by(self.model.profile_id)
            res = await self.session.execute(query)
            statistics = res.scalars().all()

            for idx, stat in enumerate(statistics, start=1):
                query = (
                    update(self.model)
                    .where(self.model.id == stat.id)
                    .values(place=idx)
                )
                await self.session.execute(query)

            await self.session.commit()

    async def delete_all_statistics(self) -> None:
        """Удаление всех данных из таблицы"""
        async with self.session.begin():
            assert (
                self.model is not Statistic
            ), "Попытка удалить общую статистику"

            if self.model is Statistic:
                return

            query = delete(self.model)
            await self.session.execute(query)
            await self.session.commit()

    async def _sub_create(self, pk: int, place: int) -> Statistic:
        """Вспомогательная функция создания объекта"""
        statistic = self.model(
            profile_id=pk,
            place=place,
        )
        self.session.add(statistic)
        await self.session.commit()
        return statistic

    async def _sub_get_count(self) -> int:
        """Вспомогательная функция подсчета объектов"""
        query = select(func.count(self.model.id))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _sub_get_by_profile(self, profile_pk: int) -> Statistic | None:
        """Вспомогательная функция получения объекта"""
        query = (
            select(self.model)
            .join(self.model.profile)
            .outerjoin(Profile.title)
            .options(joinedload(self.model.profile).joinedload(Profile.title))
            .where(self.model.profile_id == profile_pk)
        )
        res = await self.session.execute(query)
        orm_result = res.fetchone()

        if orm_result is None:
            return None

        return orm_result[0]


@dataclass
class ORMProfileTitleService(IProfileTitleService):
    session: AsyncSession

    async def get_or_create_by_profile(
        self,
        profile_pk: int,
    ) -> ProfileTitleDTO:
        """Вызывается внутри другой сессии, не напрямую"""
        async with self.session.begin():
            query = select(BestPlayerTitle).where(
                BestPlayerTitle.profile_id == profile_pk
            )
            res = await self.session.execute(query)
            title = res.fetchone()

            if title is None:  # если не найдена
                title = BestPlayerTitle(
                    best_of_the_day=0,
                    best_of_the_month=0,
                    profile_id=profile_pk,
                )
                self.session.add(title)
                return await orm_profile_title_to_dto(title)
            return await orm_profile_title_to_dto(title[0])

    async def patch(self, profile_pk: int, **fields) -> ProfileTitleDTO:
        """Вызывается внутри другой сессии, не напрямую"""
        async with self.session.begin():
            query = (
                update(BestPlayerTitle)
                .where(BestPlayerTitle.profile_id == profile_pk)
                .values(**fields)
                .returning(BestPlayerTitle)
            )
            result = await self.session.execute(query)
            orm_result = result.fetchone()
            return await orm_profile_title_to_dto(orm_result[0])
