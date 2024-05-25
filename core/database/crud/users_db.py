from dataclasses import dataclass

from fastapi import HTTPException

from starlette import status

from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.sql import func

from mobile.users.models import Profile
from mobile.users.models import Statistic
from mobile.users.schema import SetStatisticsSchema, GetStatisticsSchema

from .utils import get_last_place


@dataclass
class ProfileCRUD:
    session: AsyncSession

    async def create(self, device_uuid: str) -> Profile:
        try:
            async with self.session.begin():
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device_uuid,
                )

                self.session.add(new_profile)
                await self.session.flush()
                new_profile.name = f"Игрок-{new_profile.id}"

                await StatisticsCRUD.create(new_profile.id, self.session)

                await self.session.flush()
                return new_profile
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для этого устройства уже создан профиль",
            )
        except (InvalidRequestError, AttributeError):
            pass

    async def get(self, pk: int) -> Profile:
        async with self.session.begin():
            try:
                query = select(
                    Profile.id,
                    Profile.name,
                ).where(Profile.id == pk)
                res = await self.session.execute(query)
                profile_id, profile_name, *_ = res.fetchone()
                return Profile(
                    id=profile_id,
                    name=profile_name,
                )
            except TypeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Такой профиль не найден",
                )

    async def patch(self, pk: int, **kwargs) -> Profile:
        async with self.session.begin():
            try:
                query = (
                    update(Profile)
                    .where(Profile.id == pk)
                    .values(**kwargs)
                    .returning(
                        Profile.id,
                        Profile.name,
                    )
                )
                res = await self.session.execute(query)
                profile_id, profile_name = res.fetchone()
                return Profile(
                    id=profile_id,
                    name=profile_name,
                )
            except TypeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Такой профиль не найден",
                )


@dataclass
class StatisticsCRUD:
    session: AsyncSession

    @staticmethod
    async def create(pk: int, session: AsyncSession) -> None:
        last_place = await get_last_place(session)
        profile_statistic = Statistic(
            profile_id=pk,
            place=last_place,
        )
        session.add(profile_statistic)

    async def patch(
            self,
            pk: int,
            game_stat: SetStatisticsSchema,
    ):
        try:
            async with self.session.begin():
                query = select(
                    Statistic.id,
                    Statistic.place,
                    Statistic.score,
                    Statistic.rights,
                    Statistic.wrongs,
                    Statistic.games
                ).where(Statistic.profile_id == pk)
                res = await self.session.execute(query)
                orm_result = res.fetchone()
                current_stat = GetStatisticsSchema.model_validate(
                    orm_result, from_attributes=True
                )
                print(f"\n\n{current_stat=}")
                print(f'\n{game_stat.score=}\n')
                query = (
                    update(Statistic)
                    .where(Statistic.profile_id == pk)
                    .values(
                        score=current_stat.score + game_stat.score,
                        rights=current_stat.rights + game_stat.rights,
                        wrongs=current_stat.wrongs + game_stat.wrongs,
                        games=current_stat.games + 1
                    )
                    .returning(
                        Statistic.id,
                        Statistic.games,
                        Statistic.place,
                        Statistic.score,
                        Statistic.rights,
                        Statistic.wrongs,

                    )
                )
                result = await self.session.execute(query)
                # await self.session.commit()
                orm_new_stat = result.fetchone()
                new_stat = GetStatisticsSchema.model_validate(
                    orm_new_stat, from_attributes=True
                )
                new_place = await change_users_places(
                    pk, current_stat.place, new_stat, self.session
                )
                # await self.session.flush()


        except Exception as e:
            print(f"\nGET EXEPTION {e}")


async def change_users_places(
        pk: int,
        old_place: int,
        new_stat: GetStatisticsSchema,
        session: AsyncSession,
):
    print(f"p0")
    subquery = (
        select(
            Statistic.id,
            Statistic.score,
            func.row_number().over(order_by=desc(Statistic.score)).label('rank')
        ).subquery()
    )
    print(f"p1")
    query = (
        select(subquery.c.rank)
        .where(subquery.c.id == new_stat.id)
    )

    result = await session.execute(query)
    rank = result.fetchone()[0]
    print(f"{rank=}\n{old_place=}")

    subquery = (
        select(
            Statistic.id,
            Statistic.score,
            Statistic.place,
            func.row_number().over(order_by=desc(Statistic.score)).label('rank')
        ).subquery()
    )

    start = rank if rank < old_place else old_place
    end = old_place if old_place > rank else rank
    if rank < old_place:
        shift = "up"
    else:
        shift = "down"
    query = (
        select(subquery.c.id, subquery.c.score, subquery.c.place)
        .order_by(subquery.c.place)
        .where(subquery.c.rank.between(start, end))
    )

    result = await session.execute(query)
    scores = result.all()
    print(f"\n{scores=}")
    for s in scores:
        print(f"\n{s=}")

    if shift == "up":
        for s in scores:
            q = select(Statistic).where(Statistic.id == s.id, Statistic.profile_id != pk)
            result = await session.execute(q)
            scores = result.all()
            print(f'\n\n{scores=}\n')
            await session.execute(
                update(Statistic)
                .where(Statistic.id == s.id, Statistic.profile_id != pk)
                .values(place=Statistic.place + 1)
            )
            await session.execute(
                update(Statistic)
                .where(Statistic.id == pk)
                .values(place=rank)
            )
        await session.commit()
    if shift == "down":
        for s in scores:
            await session.execute(
                update(Statistic)
                .where(Statistic.id == s.id, Statistic.id != pk)
                .values(place=Statistic.place - 1)
            )
            await session.execute(
                update(Statistic)
                .where(Statistic.id == pk)
                .values(place=rank)
            )
        await session.commit()

