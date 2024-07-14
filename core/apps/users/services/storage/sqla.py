from dataclasses import dataclass

from sqlalchemy import (
    desc,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from core.apps.users.dto import (
    ProfileDTO,
    StatisticDTO,
)
from core.apps.users.dto.converter import (
    orm_profile_to_dto,
    orm_statistics_to_dto,
)
from core.apps.users.models import (
    Profile,
    Statistic,
)
from core.apps.users.services.storage.base import (
    IProfileService,
    IStatisticService,
)


@dataclass
class ORMProfileService(IProfileService):
    session: AsyncSession

    async def create(self, device: str) -> ProfileDTO:
        async with self.session.begin():
            new_profile = Profile(
                name="Игрок",
                device_uuid=device,
            )
            self.session.add(new_profile)
            await self.session.commit()
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
            return await orm_profile_to_dto(orm_result[0])

    async def get_by_device(self, token: str) -> ProfileDTO:
        async with self.session.begin():
            query = select(Profile).where(Profile.device_uuid == token)
            result = await self.session.execute(query)
            orm_result = result.fetchone()
            return await orm_profile_to_dto(orm_result[0])


@dataclass
class ORMStatisticService(IStatisticService):
    session: AsyncSession

    async def create(self, pk: int) -> StatisticDTO:
        async with self.session.begin():
            query = select(func.count()).select_from(Statistic)
            res = await self.session.execute(query)
            last_place = res.fetchone()[0] + 1

            profile_statistic = Statistic(
                profile_id=pk,
                place=last_place,
            )
            self.session.add(profile_statistic)
            await self.session.commit()
            return profile_statistic

    async def get_by_id(self, pk: int) -> StatisticDTO:
        async with self.session.begin():
            query = select(Statistic).where(Statistic.profile_id == pk)
            res = await self.session.execute(query)
            orm_result = res.fetchone()
            return await orm_statistics_to_dto(orm_result[0])

    async def replace_profiles(self, new_place, old_place) -> None:
        async with self.session.begin():
            if new_place > old_place:
                query = (
                    update(Statistic)
                    .where(
                        (Statistic.place <= new_place)
                        & (Statistic.place > old_place)
                    )
                    .values(
                        place=Statistic.place - 1,
                        trend=Statistic.trend + 1,
                    )
                    .returning(Statistic)
                )
            else:
                query = (
                    update(Statistic)
                    .where(
                        (Statistic.place >= new_place)
                        & (Statistic.place < old_place)
                    )
                    .values(
                        place=Statistic.place + 1,
                        trend=Statistic.trend - 1,
                    )
                    .returning(Statistic)
                )
            await self.session.execute(query)
            await self.session.commit()

    async def patch(self, pk: int, **fields) -> StatisticDTO:
        async with self.session.begin():
            query = (
                update(Statistic)
                .where(Statistic.id == pk)
                .values(**fields)
                .returning(Statistic)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            orm_result = result.fetchone()
            return await orm_statistics_to_dto(orm_result[0])

    async def get_user_rank(
        self,
        profile_pk: int,
    ) -> int:
        async with self.session.begin():
            subquery = select(
                Statistic,
                func.row_number()
                .over(
                    order_by=[
                        desc(Statistic.score),
                        desc(Statistic.games),
                        Statistic.id,
                    ]
                )
                .label("rank"),
            ).subquery()
            query = select(subquery.c.rank).where(
                subquery.c.profile_id == profile_pk
            )

            result = await self.session.execute(query)
            rank = result.fetchone()[0]

            return rank

    async def get_replaced_users(
        self,
        current_place: int,
        new_place: int,
    ) -> list[StatisticDTO]:
        async with self.session.begin():
            start, end = (
                (current_place, new_place)
                if current_place < new_place
                else (new_place, current_place)
            )
            subquery = select(
                Statistic,
                func.row_number()
                .over(
                    order_by=[
                        desc(Statistic.score),
                    ]
                )
                .label("rank"),
            ).subquery()
            query = (
                select(Statistic)
                .join(subquery, subquery.c.id == Statistic.id)
                .order_by(subquery.c.place)
                .where(subquery.c.rank.between(start, end))
            )

            result = await self.session.execute(query)
            orm_res = result.all()

            return [await orm_statistics_to_dto(row[0]) for row in orm_res]

    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[StatisticDTO]:
        query = (
            select(Statistic)
            .order_by(Statistic.place, Statistic.games.desc(), Statistic.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        ladder = result.scalars().all()
        return [await orm_statistics_to_dto(obj) for obj in ladder]

    async def get_count(self) -> int:
        query = select(func.count(Statistic.id))
        result = await self.session.execute(query)
        return result.scalar_one()
