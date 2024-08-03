import random as python_random
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.sql.functions import random

from apps.quiz.dto import QuestionDTO
from apps.quiz.dto.converter import (
    category_orm_to_dto,
    complaint_orm_to_dto,
    list_category_orm_to_dto,
    list_question_orm_to_dto,
    question_orm_to_dto,
)
from apps.quiz.dto.dto import (
    CategoryComplaintDTO,
    ComplaintDTO,
)
from apps.quiz.exceptions import (
    CategoryComplaintDoesNotExists,
    QuestionDoesNotExists,
)
from apps.quiz.models import (
    CategoryComplaint,
    Complaint,
    Question,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.users.dto import ProfileDTO
from core.database.db import Database


@dataclass
class ORMQuestionsService(IQuestionService):
    db: Database

    async def get_random(self, limit: int) -> list[QuestionDTO]:
        async with self.db.get_session() as session:
            q = aliased(Question)
            query = (
                select(
                    q,
                )
                .filter(q.published == True)
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
            return await list_question_orm_to_dto(questions)

    async def get_by_id(self, pk: int) -> QuestionDTO:
        async with self.db.get_session() as session:
            query = (
                select(Question)
                .where(Question.id == pk)
                .options(selectinload(Question.answers))
            )
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise QuestionDoesNotExists()
            return await question_orm_to_dto(orm_result[0])


@dataclass
class ORMComplaintService(IComplaintService):
    db: Database

    async def create(
        self,
        text: str,
        question: QuestionDTO,
        profile: ProfileDTO,
        category: CategoryComplaintDTO,
    ) -> ComplaintDTO:
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
            return await complaint_orm_to_dto(
                complaint, question, profile, category
            )

    async def get_by_id(self, pk: int) -> ComplaintDTO: ...

    async def list(self) -> ComplaintDTO: ...


@dataclass
class ORMCategoryComplaintService(ICategoryComplaintService):
    db: Database

    async def list(self) -> list[CategoryComplaintDTO]:
        async with self.db.get_session() as session:
            query = select(CategoryComplaint)
            result = await session.execute(query)
            orm_result = result.scalars().all()

            return await list_category_orm_to_dto(orm_result)

    async def get_by_id(self, pk: int) -> CategoryComplaintDTO:
        async with self.db.get_session() as session:
            query = select(CategoryComplaint)
            result = await session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise CategoryComplaintDoesNotExists()
            return await category_orm_to_dto(orm_result[0])
