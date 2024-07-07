import random as python_random
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.sql.functions import random

from core.apps.quiz.dto import QuestionDTO
from core.apps.quiz.dto.converter import (
    category_orm_to_dto,
    complaint_orm_to_dto,
    list_category_orm_to_dto,
    list_question_orm_to_dto,
    question_orm_to_dto,
)
from core.apps.quiz.dto.dto import (
    CategoryComplaintDTO,
    ComplaintDTO,
)
from core.apps.quiz.exceptions import (
    CategoryComplaintDoesNotExists,
    QuestionDoesNotExists,
)
from core.apps.quiz.models import (
    CategoryComplaint,
    Complaint,
    Question,
)
from core.apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from core.apps.users.dto import ProfileDTO


@dataclass
class ORMQuestionsService(IQuestionService):
    session: AsyncSession

    async def get_random(self, limit: int) -> list[QuestionDTO]:
        async with self.session.begin():
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
            result = await self.session.execute(query)
            questions = result.scalars().all()
            for question in questions:
                question.answers = sorted(
                    question.answers, key=lambda x: python_random.random()
                )
            return await list_question_orm_to_dto(questions)

    async def get_by_id(self, pk: int) -> QuestionDTO:
        async with self.session.begin():
            query = (
                select(Question)
                .where(Question.id == pk)
                .options(selectinload(Question.answers))
            )
            result = await self.session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise QuestionDoesNotExists()
            return await question_orm_to_dto(orm_result[0])


@dataclass
class ORMComplaintService(IComplaintService):
    session: AsyncSession

    async def create(
        self,
        text: str,
        question: QuestionDTO,
        profile: ProfileDTO,
        category: CategoryComplaintDTO,
    ) -> ComplaintDTO:
        async with self.session.begin():
            complaint = Complaint(
                profile_id=profile.id,
                question_id=question.id,
                text=text,
                created_at=datetime.now(),
                solved=False,
                category_id=category.id,
            )
            self.session.add(complaint)
            await self.session.commit()
            return await complaint_orm_to_dto(
                complaint, question, profile, category
            )

    async def get_by_id(self, pk: int) -> ComplaintDTO: ...

    async def list(self) -> ComplaintDTO: ...


@dataclass
class ORMCategoryComplaintService(ICategoryComplaintService):
    session: AsyncSession

    async def list(self) -> list[CategoryComplaintDTO]:
        async with self.session.begin():
            query = select(CategoryComplaint)
            result = await self.session.execute(query)
            orm_result = result.scalars().all()

            return await list_category_orm_to_dto(orm_result)

    async def get_by_id(self, pk: int) -> CategoryComplaintDTO:
        async with self.session.begin():
            query = select(CategoryComplaint)
            result = await self.session.execute(query)
            orm_result = result.fetchone()

            if orm_result is None:
                raise CategoryComplaintDoesNotExists()
            return await category_orm_to_dto(orm_result[0])
