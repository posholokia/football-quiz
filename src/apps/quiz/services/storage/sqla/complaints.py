from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import func

from apps.quiz.converter import (
    category_orm_to_entity,
    complaint_orm_to_entity,
    complaint_with_related_orm_to_entity,
    list_category_orm_to_entity,
)
from apps.quiz.exceptions import CategoryComplaintDoesNotExists
from apps.quiz.models import (
    CategoryComplaint,
    CategoryComplaintEntity,
    Complaint,
    ComplaintEntity,
    QuestionEntity,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
)
from apps.users.models import ProfileEntity
from core.database.db import Database


@dataclass
class ORMComplaintService(IComplaintService):
    db: Database

    async def create(
        self,
        text: str,
        question: QuestionEntity,
        profile: ProfileEntity,
        category: CategoryComplaintEntity,
    ) -> ComplaintEntity:
        async with self.db.get_session() as session:
            complaint = Complaint(
                profile_id=profile.id,
                question_id=question.id,
                text=text,
                created_at=datetime.now(),
                solved=False,
                category_id=category.id,
            )
            session.add(complaint)
            await session.commit()
            return await complaint_orm_to_entity(
                complaint, question, profile, category
            )

    async def get_by_id(self, pk: int) -> ComplaintEntity: ...

    async def get_list(
        self,
        offset: int,
        limit: int = 100,
    ) -> list[ComplaintEntity]:
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
            complaints = result.fetchall()

            return [
                await complaint_with_related_orm_to_entity(c[0])
                for c in complaints
            ]

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

    async def list(self) -> list[CategoryComplaintEntity]:
        async with self.db.get_ro_session() as session:
            query = select(CategoryComplaint)
            result = await session.execute(query)
            orm_result = result.scalars().all()

            return await list_category_orm_to_entity(orm_result)

    async def get_by_id(self, pk: int) -> CategoryComplaintEntity:
        async with self.db.get_ro_session() as session:
            query = select(CategoryComplaint)
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise CategoryComplaintDoesNotExists()
            return await category_orm_to_entity(orm_result[0])
