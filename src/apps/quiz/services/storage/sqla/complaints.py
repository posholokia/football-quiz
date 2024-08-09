from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import func

from apps.quiz.exceptions import CategoryComplaintDoesNotExists
from apps.quiz.models import (
    CategoryComplaint,
    Complaint,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
)
from core.database.db import Database


@dataclass
class ORMComplaintService(IComplaintService):
    db: Database

    async def create(
        self,
        text: str,
        question_id: int,
        profile_id: int,
        category_id: int,
    ) -> Complaint:
        async with self.db.get_session() as session:
            complaint = Complaint(
                profile_id=profile_id,
                question_id=question_id,
                text=text,
                created_at=datetime.now(),
                solved=False,
                category_id=category_id,
            )
            session.add(complaint)
            await session.commit()
            return complaint

    async def get_by_id(self, pk: int) -> Complaint: ...

    async def get_list(
        self,
        offset: int,
        limit: int = 100,
    ) -> list[Complaint]:
        async with self.db.get_ro_session() as session:
            query = (
                select(Complaint)
                .options(
                    selectinload(Complaint.profile),
                    selectinload(Complaint.question),
                    selectinload(Complaint.category),
                )
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            complaints = result.scalars().fetchall()

            return complaints

    async def get_count(self) -> int:
        async with self.db.get_ro_session() as session:
            query = select(func.count(Complaint.id))
            result = await session.execute(query)
            return result.scalar_one()

    async def delete(self, pk: int) -> None:
        async with self.db.get_session() as session:
            query = delete(Complaint).where(Complaint.id == pk)
            await session.execute(query)


@dataclass
class ORMCategoryComplaintService(ICategoryComplaintService):
    db: Database

    async def list(self) -> list[CategoryComplaint]:
        async with self.db.get_ro_session() as session:
            query = select(CategoryComplaint)
            result = await session.execute(query)
            orm_result = result.scalars().all()

            return orm_result

    async def get_by_id(self, pk: int) -> CategoryComplaint:
        async with self.db.get_ro_session() as session:
            query = select(CategoryComplaint).where(CategoryComplaint.id == pk)
            result = await session.execute(query)
            orm_result = result.scalar()

            if orm_result is None:
                raise CategoryComplaintDoesNotExists()
            return orm_result


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
        res = await repo.get_list(0, 1)
        for complaint in res:
            print(complaint.to_entity())
            print(complaint.category_id)
            pass

        cat_repo: ORMCategoryComplaintService = container.resolve(
            ICategoryComplaintService
        )
        cat = await cat_repo.get_by_id(14)
        print(cat.to_entity())

    asyncio.run(main())
