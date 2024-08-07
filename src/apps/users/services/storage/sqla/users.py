from dataclasses import dataclass

from sqlalchemy import (
    and_,
    select,
)
from sqlalchemy.sql import true

from apps.users.converter import orm_user_to_entity
from apps.users.exceptions.auth import UserDoesNotExists
from apps.users.models import (
    User,
    UserEntity,
)
from apps.users.services.storage.base import IUserService
from core.database.db import Database


@dataclass
class ORMUserService(IUserService):
    db: Database

    async def get_by_username(self, username: str) -> UserEntity | None:
        async with self.db.get_ro_session() as session:
            query = select(User).where(User.username == username)
            res = await session.execute(query)
            user_orm = res.fetchone()
            if user_orm is None:
                return None
            return await orm_user_to_entity(user_orm[0])

    async def get_by_id(self, pk: int) -> UserEntity:
        async with self.db.get_ro_session() as session:
            query = select(User).where(
                and_(User.id == pk, User.is_active == true())
            )
            res = await session.execute(query)
            user_orm = res.fetchone()

            if user_orm is None:
                raise UserDoesNotExists()
            return await orm_user_to_entity(user_orm[0])
