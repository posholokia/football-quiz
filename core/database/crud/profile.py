from dataclasses import dataclass

from fastapi import HTTPException

from starlette import status

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from mobile.users.models import Profile


@dataclass
class ProfileCRUD:
    session: AsyncSession

    async def create(self, device_uuid) -> Profile:
        async with self.session.begin():
            try:
                new_profile = Profile(
                    name="Игрок",
                    device_uuid=device_uuid,
                )

                self.session.add(new_profile)
                await self.session.flush()
                new_profile.name = f"Игрок-{new_profile.id}"
                await self.session.commit()
                return new_profile
            except IntegrityError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Для этого устройства уже создан профиль",
                )

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

    async def patch(self, pk, **kwargs) -> Profile:
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
