import random as python_random
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    delete,
    select,
    tablesample,
    true,
)
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.sql.functions import (
    func,
    random,
)

from apps.quiz.converter import (
    category_orm_to_entity,
    complaint_orm_to_entity,
    list_category_orm_to_entity,
    list_orm_question_to_entity,
    question_orm_to_admin_dto,
    question_orm_to_entity,
)
from apps.quiz.exceptions import (
    CategoryComplaintDoesNotExists,
    QuestionDoesNotExists,
)
from apps.quiz.models import (
    CategoryComplaint,
    CategoryComplaintEntity,
    Complaint,
    ComplaintEntity,
    Question,
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.users.models import ProfileEntity
from core.database.db import Database


@dataclass
class ORMQuestionsService(IQuestionService):
    db: Database

    async def get_random(self, limit: int) -> list[QuestionEntity]:
        async with self.db.get_ro_session() as session:
            q = aliased(Question, tablesample(Question, func.bernoulli(0.2)))
            query = (
                select(
                    q,
                )
                .filter(q.published == true())
                .order_by(random())
                .limit(limit)
                .options(selectinload(q.answers))
            )
            result = await session.execute(query)
            questions = result.scalars().all()
            for question in questions:
                question.answers = sorted(
                    question.answers, key=lambda x: python_random.random()
                )
            return await list_orm_question_to_entity(questions)

    async def get_by_id(self, pk: int) -> QuestionEntity:
        async with self.db.get_ro_session() as session:
            query = (
                select(Question)
                .where(Question.id == pk)
                .options(selectinload(Question.answers))
            )
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise QuestionDoesNotExists()
            return await question_orm_to_entity(orm_result[0])

    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[QuestionAdminDTO]:
        async with self.db.get_ro_session() as session:
            subquery = (
                select(
                    Question.id,
                    func.count(Complaint.id).label("complaints_count"),
                )
                .outerjoin(Complaint, Complaint.question_id == Question.id)
                .group_by(Question.id)
                .subquery()
            )

            query = (
                select(Question, subquery.c.complaints_count)
                .outerjoin(subquery, subquery.c.id == Question.id)
                .options(selectinload(Question.answers))
                .offset(offset)
                .limit(limit)
            )

            if search is not None:
                query = query.filter(Question.text.ilike(f"%{search}%"))

            result = await session.execute(query)
            questions = result.fetchall()
            return [await question_orm_to_admin_dto(q) for q in questions]

    async def get_count(self, search: str | None = None) -> int:
        async with self.db.get_ro_session() as session:
            query = select(func.count(Question.text))

            if search is not None:
                query = query.filter(Question.text.ilike(f"%{search}%"))

            result = await session.execute(query)
            return result.scalar_one()

    async def delete(self, pk: int) -> None:
        async with self.db.get_session() as session:
            query = delete(Question).where(Question.id == pk)
            await session.execute(query)


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

    # async def get_count_by_questions(self, question_id: int) -> int:
    #     async with self.db.get_ro_session() as session:
    #         query = select(func.count(Complaint.question_id == question_id))
    #         result = await session.execute(query)
    #         return result.scalar_one()

    async def list(self) -> ComplaintEntity: ...


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
