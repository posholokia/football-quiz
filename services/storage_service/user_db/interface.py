from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from dataclasses import dataclass

from services.storage_service.dto import StatisticDTO, ProfileDTO
from apps.users.models import Statistic, Profile
from services.storage_service.user_db.converter import statistics_orm_row_to_entity, profile_model_to_dto, \
    profile_orm_row_to_entity
from sqlalchemy.sql import func

from services.storage_service.base import IStatisticService, IProfileService


@dataclass
class ORMProfileService(IProfileService):
    session: AsyncSession

    async def create_profile(self, device: str) -> ProfileDTO:
        new_profile = Profile(
            name="Игрок",
            device_uuid=device,
        )
        self.session.add(new_profile)
        await self.session.flush()

        return await profile_model_to_dto(new_profile)

    async def patch_profile(self, pk: int, **kwargs) -> ProfileDTO:
        query = (
            update(Profile)
            .where(Profile.id == pk)
            .values(**kwargs)
            .returning(Profile)
        )
        result = await self.session.execute(query)
        orm_result = result.fetchone()

        return await profile_orm_row_to_entity(orm_result[0])

    async def get_profile(self, pk: int) -> ProfileDTO:
        query = select(Profile).where(Profile.id == pk)
        result = await self.session.execute(query)
        orm_result = result.fetchone()
        return await profile_orm_row_to_entity(orm_result[0])

    async def get_device_profile(self, token: str) -> ProfileDTO:
        query = select(Profile).where(Profile.device_uuid == token)
        result = await self.session.execute(query)
        orm_result = result.fetchone()
        return await profile_orm_row_to_entity(orm_result[0])


@dataclass
class ORMStatisticService(IStatisticService):
    session: AsyncSession

    async def create_user_statistics(self, pk: int):
        query = select(func.count()).select_from(Statistic)
        res = await self.session.execute(query)
        last_place = res.fetchone()[0] + 1

        profile_statistic = Statistic(
            profile_id=pk,
            place=last_place,
        )
        self.session.add(profile_statistic)

    async def get_user_statistics(
            self, pk: int,
    ) -> StatisticDTO:
        query = (select(Statistic).
                 where(Statistic.profile_id == pk))
        res = await self.session.execute(query)
        orm_result = res.fetchone()

        return await statistics_orm_row_to_entity(orm_result[0])

    async def update_user_statistics(
            self,
            new_stat: StatisticDTO,
    ) -> StatisticDTO:
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
        orm_result = result.fetchone()

        return await statistics_orm_row_to_entity(orm_result[0])

    async def get_user_rank(
            self,
            new_stat: StatisticDTO,
    ) -> int:
        subquery = (
            select(
                Statistic.id,
                Statistic.score,
                func.row_number().over(
                    order_by=[desc(Statistic.score), desc(Statistic.games)]
                ).label('rank')
            ).subquery()
        )
        query = (
            select(subquery.c.rank)
            .where(subquery.c.id == new_stat.id)
        )

        result = await self.session.execute(query)
        rank = result.fetchone()[0]

        return rank

    async def get_changed_statistic(
            self,
            current_place: int,
            new_place: int,
    ) -> list[StatisticDTO]:
        start, end = (current_place, new_place) \
            if current_place < new_place \
            else (new_place, current_place)
        subquery = (
            select(
                Statistic,
                func.row_number().over(
                    order_by=[desc(Statistic.score), ]
                ).label('rank')
            ).subquery()
        )
        query = (
            select(Statistic)
            .join(subquery, subquery.c.id == Statistic.id)
            .order_by(subquery.c.place)
            .where(subquery.c.rank.between(start, end))
        )

        result = await self.session.execute(query)
        orm_res = result.all()

        return [await statistics_orm_row_to_entity(row[0]) for row in orm_res]
