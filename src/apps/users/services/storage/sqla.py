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

from apps.users.converter import (
    orm_ladder_to_dto,
    orm_profile_title_to_entity,
    orm_profile_to_dto,
    orm_statistics_to_entity,
    orm_title_statistics_to_dto,
    orm_user_to_entity,
)
from apps.users.exceptions.profile import (
    AlreadyExistsProfile,
    DoesNotExistsProfile,
)
from apps.users.exceptions.statistics import StatisticDoseNotExists
from apps.users.models import (
    BestPlayerTitle,
    BestPlayerTitleEntity,
    Profile,
    ProfileEntity,
    Statistic,
    StatisticEntity,
    User,
    UserEntity,
)
from apps.users.models.dto import (
    LadderStatisticDTO,
    TitleStatisticDTO,
)
from apps.users.services.storage import (
    IProfileService,
    IStatisticService,
)
from apps.users.services.storage.base import (
    IProfileTitleService,
    IUserService,
)
from core.database.db import (
    Base,
    Database,
)


T = TypeVar("T", bound=Base)


@dataclass
class ORMProfileService(IProfileService):
    db: Database

    async def create(self, device: str) -> ProfileEntity:
        try:
            async with self.db.get_session() as session:
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device,
                )
                session.add(new_profile)
                await session.commit()
                return await orm_profile_to_dto(new_profile)

        except IntegrityError:
            raise AlreadyExistsProfile()

    async def get_or_create(self, device: str) -> ProfileEntity:
        async with self.db.get_session() as session:
            query = select(Profile).where(Profile.device_uuid == device)
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device,
                )
                session.add(new_profile)
                await session.commit()
            else:
                new_profile = orm_result[0]
            return await orm_profile_to_dto(new_profile)

    async def patch(self, pk: int, **kwargs) -> ProfileEntity:
        async with self.db.get_session() as session:
            query = (
                update(Profile)
                .where(Profile.id == pk)
                .values(**kwargs)
                .returning(Profile)
            )
            result = await session.execute(query)
            await session.commit()
            orm_result = result.fetchone()
            return await orm_profile_to_dto(orm_result[0])

    async def get_by_id(self, pk: int) -> ProfileEntity:
        async with self.db.get_session() as session:
            query = select(Profile).where(Profile.id == pk)
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise DoesNotExistsProfile()

            return await orm_profile_to_dto(orm_result[0])

    async def get_by_device(self, token: str) -> ProfileEntity:
        async with self.db.get_session() as session:
            query = select(Profile).where(Profile.device_uuid == token)
            result = await session.execute(query)
            orm_result = result.fetchone()
            return await orm_profile_to_dto(orm_result[0])


@dataclass
class ORMStatisticService(IStatisticService, Generic[T]):
    db: Database
    model: Type[T]

    async def create(self, pk: int, place: int) -> StatisticEntity:
        async with self.db.get_session() as session:
            stat = await self._sub_create(session, pk, place)
            return await orm_statistics_to_entity(stat)

    async def get_by_profile(self, profile_pk: int) -> TitleStatisticDTO:
        async with self.db.get_session() as session:
            stat = await self._sub_get_by_profile(session, profile_pk)

            if stat is None:
                raise StatisticDoseNotExists(
                    detail=f"Статистика для игрока с id: {profile_pk} не найдена"
                )
            return await orm_title_statistics_to_dto(stat)

    async def get_by_place(self, place: int) -> StatisticEntity | None:
        async with self.db.get_session() as session:
            query = select(self.model).where(self.model.place == place)
            res = await session.execute(query)
            orm_result = res.fetchone()

            if orm_result is None:
                return None
            return await orm_statistics_to_entity(orm_result[0])

    async def get_or_create_by_profile(
        self, profile_pk: int
    ) -> StatisticEntity:
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

            return await orm_statistics_to_entity(statistic)

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

    async def patch(self, pk: int, **fields) -> StatisticEntity:
        async with self.db.get_session() as session:
            query = (
                update(self.model)
                .where(self.model.id == pk)
                .values(**fields)
                .returning(self.model)
            )
            result = await session.execute(query)
            await session.commit()
            orm_result = result.fetchone()
            return await orm_statistics_to_entity(orm_result[0])

    async def get_user_rank(
        self,
        profile_pk: int,
    ) -> int:
        """Положение юзера в ладдере на основе его статистики"""
        async with self.db.get_session() as session:
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
    ) -> list[LadderStatisticDTO]:
        """Получение топа игроков"""
        async with self.db.get_session() as session:
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
            ladder = result.scalars().all()
            return [await orm_ladder_to_dto(obj) for obj in ladder]

    async def get_count(self) -> int:
        """Общее количество игроков со статистикой"""
        async with self.db.get_session() as session:
            return await self._sub_get_count(session)

    async def get_count_positive_score(self) -> int:
        """Количество игроков с не отрицательными очками"""
        async with self.db.get_session() as session:
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
        orm_result = res.fetchone()

        if orm_result is None:
            return None

        return orm_result[0]


@dataclass
class ORMProfileTitleService(IProfileTitleService):
    db: Database

    async def get_or_create_by_profile(
        self,
        profile_pk: int,
    ) -> BestPlayerTitleEntity:
        """Вызывается внутри другой сессии, не напрямую"""
        async with self.db.get_session() as session:
            query = select(BestPlayerTitle).where(
                BestPlayerTitle.profile_id == profile_pk
            )
            res = await session.execute(query)
            title = res.fetchone()

            if title is None:  # если не найдена
                title = BestPlayerTitle(
                    best_of_the_day=0,
                    best_of_the_month=0,
                    profile_id=profile_pk,
                )
                session.add(title)
                return await orm_profile_title_to_entity(title)
            return await orm_profile_title_to_entity(title[0])

    async def patch(self, profile_pk: int, **fields) -> BestPlayerTitleEntity:
        """Вызывается внутри другой сессии, не напрямую"""
        async with self.db.get_session() as session:
            query = (
                update(BestPlayerTitle)
                .where(BestPlayerTitle.profile_id == profile_pk)
                .values(**fields)
                .returning(BestPlayerTitle)
            )
            result = await session.execute(query)
            orm_result = result.fetchone()
            return await orm_profile_title_to_entity(orm_result[0])


@dataclass
class ORMUserService(IUserService):
    db: Database

    async def get_by_username(self, username: str) -> UserEntity | None:
        async with self.db.get_session() as session:
            query = select(User).where(User.username == username)
            res = await session.execute(query)
            user_orm = res.fetchone()
            if user_orm is None:
                return None
            return await orm_user_to_entity(user_orm[0])
