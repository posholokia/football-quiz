from dataclasses import dataclass
from typing import Type

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.selectable import Select

from apps.quiz.models import Complaint
from apps.users.exceptions.profile import DoesNotExistsProfile
from apps.users.models import ProfileEntity
from apps.users.services.storage import IProfileService
from core.database.db import Database
from core.database.repository.base import TModel
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMProfileService(CommonRepository, IProfileService):
    db: Database
    model: Type[TModel]

    async def update(self, pk: int, **fields) -> ProfileEntity:
        profile = await super().update(pk, **fields)

        if profile is None:
            raise DoesNotExistsProfile(detail=f"Профиль с id={pk} не найден")

        return profile

    async def get_count(self, search: str | None = None) -> int:
        async with self.db.get_ro_session() as session:
            query = select(func.count(self.model.name))

            if search is not None:
                query = query.filter(self.model.name.ilike(f"%{search}%"))

            result = await session.execute(query)
            return result.scalar_one()

    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[tuple[ProfileEntity, int]]:
        async with self.db.get_ro_session() as session:
            query = (
                self._sub_get_with_complaints_count()
                .offset(offset)
                .limit(limit)
            )

            if search is not None:
                query = query.filter(self.model.name.ilike(f"%{search}%"))

            result = await session.execute(query)
            profiles = result.fetchall()

            return [(p.to_entity(), c) for p, c in profiles]

    async def get_with_complaints_count_by_id(
        self,
        pk: int,
    ) -> tuple[ProfileEntity, int]:
        async with self.db.get_ro_session() as session:
            query = self._sub_get_with_complaints_count().where(
                self.model.id == pk
            )

            result = await session.execute(query)
            profile = result.fetchone()

            if profile is None:
                raise DoesNotExistsProfile(
                    detail=f"Профиль с id={pk} не найден"
                )
            return profile[0].to_entity(), profile[1]

    def _sub_get_with_complaints_count(self) -> Select:
        subquery = (
            select(
                self.model.id,
                func.count(Complaint.id).label("complaints_count"),
            )
            .outerjoin(Complaint, Complaint.profile_id == self.model.id)
            .group_by(self.model.id)
            .subquery()
        )

        query = (
            select(self.model, subquery.c.complaints_count)
            .outerjoin(
                subquery,
                subquery.c.id == self.model.id,  # type: ignore
            )
            .options(selectinload(self.model.statistic))
            .order_by(self.model.id)
        )
        return query
