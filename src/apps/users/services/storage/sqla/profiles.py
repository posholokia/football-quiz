from dataclasses import dataclass

from sqlalchemy import (
    exists,
    select,
    update,
)

from apps.users.converter import orm_profile_to_entity
from apps.users.exceptions.profile import DoesNotExistsProfile
from apps.users.models import (
    Profile,
    ProfileEntity,
)
from apps.users.services.storage import IProfileService
from core.database.db import Database


@dataclass
class ORMProfileService(IProfileService):
    db: Database

    async def create(self, device: str) -> ProfileEntity:
        async with self.db.get_session() as session:
            new_profile = Profile(
                name="Игрок",
                device_uuid=device,
            )
            session.add(new_profile)
            await session.commit()
            return await orm_profile_to_entity(new_profile)

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
            return await orm_profile_to_entity(new_profile)

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
            return await orm_profile_to_entity(orm_result[0])

    async def get_by_id(self, pk: int) -> ProfileEntity:
        async with self.db.get_ro_session() as session:
            query = select(Profile).where(Profile.id == pk)
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise DoesNotExistsProfile()

            return await orm_profile_to_entity(orm_result[0])

    async def get_by_device(self, token: str) -> ProfileEntity:
        async with self.db.get_ro_session() as session:
            query = select(Profile).where(Profile.device_uuid == token)
            result = await session.execute(query)
            orm_result = result.fetchone()
            return await orm_profile_to_entity(orm_result[0])

    async def exists_by_token(self, token: str) -> bool:
        async with self.db.get_ro_session() as session:
            query = select(exists().where(Profile.device_uuid == token))
            return await session.scalar(query)
