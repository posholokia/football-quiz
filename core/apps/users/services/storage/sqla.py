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

    async def patch(self, new_stat: StatisticDTO) -> StatisticDTO:
        async with self.session.begin():
            query = (
                update(Statistic)
                .where(Statistic.id == new_stat.id)
                .values(
                    games=new_stat.games,
                    score=new_stat.score,
                    place=new_stat.place,
                    rights=new_stat.rights,
                    wrongs=new_stat.wrongs,
                )
                .returning(Statistic)
            )
            result = await self.session.execute(query)
            await self.session.commit()
            orm_result = result.fetchone()
            return await orm_statistics_to_dto(orm_result[0])

    async def get_user_rank(
        self,
        new_stat: StatisticDTO,
    ) -> int:
        async with self.session.begin():
            subquery = select(
                Statistic.id,
                Statistic.score,
                func.row_number()
                .over(order_by=[desc(Statistic.score), desc(Statistic.games)])
                .label("rank"),
            ).subquery()
            query = select(subquery.c.rank).where(subquery.c.id == new_stat.id)

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
