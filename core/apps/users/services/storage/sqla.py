from dataclasses import dataclass
from typing import (
    Generic,
    Type,
    TypeVar,
)

from sqlalchemy import (
    and_,
    desc,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
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
from core.apps.users.exceptions.profile import (
    AlreadyExistsProfile,
    DoesNotExistsProfile,
)
from core.apps.users.models import Profile
from core.apps.users.services.storage.base import (
    IProfileService,
    IStatisticService,
)
from core.config.database.db import Base


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
            profile_statistic = self.model(
                profile_id=pk,
                place=place,
            )
            self.session.add(profile_statistic)
            await self.session.commit()
            return profile_statistic

    async def get_by_profile(self, profile_pk: int) -> StatisticDTO:
        async with self.session.begin():
            query = select(self.model).where(
                self.model.profile_id == profile_pk
            )
            res = await self.session.execute(query)
            orm_result = res.fetchone()
            return await orm_statistics_to_dto(orm_result[0])

    async def replace_profiles(self, new_place, old_place) -> None:
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
                    .returning(self.model)
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
                    .returning(self.model)
                )
            await self.session.execute(query)
            await self.session.commit()

    async def down_place_negative_score(self) -> None:
        async with self.session.begin():
            query = (
                update(self.model)
                .where(self.model.score < 0)
                .values(
                    place=self.model.place + 1,
                    trend=self.model.trend - 1,
                )
                .returning(self.model)
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
        async with self.session.begin():
            subquery = select(
                self.model,
                func.row_number()
                .over(
                    order_by=[
                        desc(self.model.score),
                        desc(self.model.games),
                        self.model.id,
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

    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[StatisticDTO]:
        async with self.session.begin():
            query = (
                select(self.model)
                .order_by(
                    self.model.place, self.model.games.desc(), self.model.id
                )
                .offset(offset)
                .limit(limit)
            )
            result = await self.session.execute(query)
            ladder = result.scalars().all()
            return [await orm_statistics_to_dto(obj) for obj in ladder]

    async def get_count(self) -> int:
        async with self.session.begin():
            query = select(func.count(self.model.id))
            result = await self.session.execute(query)
            return result.scalar_one()

    async def get_count_positive_score(self) -> int:
        async with self.session.begin():
            query = (
                select(func.count())
                .select_from(self.model)
                .where(self.model.score >= 0)
            )
            result = await self.session.execute(query)
            return result.scalar_one()
