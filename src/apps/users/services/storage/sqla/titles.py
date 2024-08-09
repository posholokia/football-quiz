from dataclasses import dataclass

from sqlalchemy import (
    select,
    update,
)

from apps.users.models import BestPlayerTitle
from apps.users.services.storage.base import IProfileTitleService
from core.database.db import Database


@dataclass
class ORMProfileTitleService(IProfileTitleService):
    db: Database

    async def get_or_create_by_profile(
        self,
        profile_pk: int,
    ) -> BestPlayerTitle:
        """Вызывается внутри другой сессии, не напрямую"""
        async with self.db.get_session() as session:
            query = select(BestPlayerTitle).where(
                BestPlayerTitle.profile_id == profile_pk
            )
            res = await session.execute(query)
            title = res.scalar()

            if title is None:  # если не найдена
                title = BestPlayerTitle(
                    best_of_the_day=0,
                    best_of_the_month=0,
                    profile_id=profile_pk,
                )
                session.add(title)

            return title

    async def patch(self, profile_pk: int, **fields) -> BestPlayerTitle:
        """Вызывается внутри другой сессии, не напрямую"""
        async with self.db.get_session() as session:
            query = (
                update(BestPlayerTitle)
                .where(BestPlayerTitle.profile_id == profile_pk)
                .values(**fields)
                .returning(BestPlayerTitle)
            )
            result = await session.execute(query)
            return result.scalar()
