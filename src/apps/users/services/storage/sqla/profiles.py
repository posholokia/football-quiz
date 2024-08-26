from dataclasses import dataclass

from sqlalchemy import (
    exists,
    select,
    update,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.selectable import Select

from apps.quiz.models import Complaint
from apps.users.exceptions.profile import DoesNotExistsProfile
from apps.users.models import Profile
from apps.users.services.storage import IProfileService
from core.database.db import Database


@dataclass
class ORMProfileService(IProfileService):
    db: Database

    async def create(self, device: str) -> Profile:
        async with self.db.get_session() as session:
            new_profile = Profile(
                name="Игрок",
                device_uuid=device,
            )
            session.add(new_profile)
            await session.commit()
            return new_profile

    async def get_or_create(self, device: str) -> Profile:
        async with self.db.get_session() as session:
            query = select(Profile).where(Profile.device_uuid == device)
            result = await session.execute(query)
            orm_result = result.scalar()

            if orm_result is None:
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device,
                )
                session.add(new_profile)
                await session.commit()

            return await new_profile

    async def patch(self, pk: int, **fields) -> Profile:
        async with self.db.get_session() as session:
            query = (
                update(Profile)
                .where(Profile.id == pk)
                .values(**fields)
                .returning(Profile)
            )
            result = await session.execute(query)
            await session.commit()
            orm_result = result.scalar()

            if orm_result is None:
                raise DoesNotExistsProfile(
                    detail=f"Профиль с id={pk} не найден"
                )

            return orm_result

    async def get_by_id(self, pk: int) -> Profile:
        async with self.db.get_ro_session() as session:
            query = select(Profile).where(Profile.id == pk)
            result = await session.execute(query)
            orm_result = result.scalar()

            if orm_result is None:
                raise DoesNotExistsProfile()

            return orm_result

    async def get_by_device(self, token: str) -> Profile:
        async with self.db.get_ro_session() as session:
            query = select(Profile).where(Profile.device_uuid == token)
            result = await session.execute(query)
            return result.scalar()

    async def exists_by_token(self, token: str) -> bool:
        async with self.db.get_ro_session() as session:
            query = select(exists().where(Profile.device_uuid == token))
            return await session.scalar(query)

    async def get_count(self, search: str | None = None) -> int:
        async with self.db.get_ro_session() as session:
            query = select(func.count(Profile.name))

            if search is not None:
                query = query.filter(Profile.name.ilike(f"%{search}%"))

            result = await session.execute(query)
            return result.scalar_one()

    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[tuple[Profile, int]]:
        async with self.db.get_ro_session() as session:
            query = (
                self._sub_get_with_complaints_count()
                .offset(offset)
                .limit(limit)
            )

            if search is not None:
                query = query.filter(Profile.name.ilike(f"%{search}%"))

            result = await session.execute(query)
            profiles = result.fetchall()

            return profiles

    async def get_with_complaints_count_by_id(
        self,
        pk: int,
    ) -> tuple[Profile, int]:
        async with self.db.get_ro_session() as session:
            query = self._sub_get_with_complaints_count().where(
                Profile.id == pk
            )

            result = await session.execute(query)
            profile = result.fetchone()

            if profile is None:
                raise DoesNotExistsProfile(
                    detail=f"Профиль с id={pk} не найден"
                )
            return profile

    @staticmethod
    def _sub_get_with_complaints_count() -> Select:
        subquery = (
            select(
                Profile.id,
                func.count(Complaint.id).label("complaints_count"),
            )
            .outerjoin(Complaint, Complaint.profile_id == Profile.id)
            .group_by(Profile.id)
            .subquery()
        )

        query = (
            select(Profile, subquery.c.complaints_count)
            .outerjoin(subquery, subquery.c.id == Profile.id)
            .options(selectinload(Profile.statistic))
            .order_by(Profile.id)
        )
        return query


if __name__ == "__main__":
    import asyncio

    from apps.users.services.storage.base import IProfileService
    from config.containers import get_container

    async def main():
        container = get_container()
        repo: ORMProfileService = container.resolve(IProfileService)
        res = await repo.create("1234")

        print(res.to_entity())

    asyncio.run(main())
