from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.quiz.models import ComplaintEntity
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
)
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMComplaintService(CommonRepository, IComplaintService):
    async def get_list(
        self, offset: int, limit: int = 100
    ) -> list[ComplaintEntity]:
        async with self._db.get_ro_session() as session:
            query = (
                select(self.model)
                .options(
                    selectinload(self.model.profile),
                    selectinload(self.model.question),
                    selectinload(self.model.category),
                )
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            orm_result = result.scalars().all()

            return [c.to_entity() for c in orm_result]


@dataclass
class ORMCategoryComplaintService(CommonRepository, ICategoryComplaintService):
    pass


if __name__ == "__main__":
    import asyncio

    from apps.quiz.services.storage.base import (
        ICategoryComplaintService,
        IComplaintService,
    )
    from apps.quiz.services.storage.sqla import (
        ORMCategoryComplaintService,
        ORMComplaintService,
    )
    from config.containers import get_container

    async def main():
        container = get_container()
        repo: ORMComplaintService = container.resolve(IComplaintService)
        await repo.get_list(0, 1)

        cat_repo: ORMCategoryComplaintService = container.resolve(
            ICategoryComplaintService
        )
        cat = await cat_repo.get_one(id=14)
        print(cat.to_entity())

    asyncio.run(main())
