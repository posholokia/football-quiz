import datetime
import random as python_random
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.sql.functions import random

from apps.quiz.models import (
    Complaint,
    Question,
)
from services.storage_service.base import (
    IComplaintService,
    IQuestionService,
)
from services.storage_service.dto import (
    ComplaintDTO,
    ProfileDTO,
    QuestionDTO,
)
from services.storage_service.quiz_db.converter import (
    complaint_model_to_dto,
    list_question_orm_row_to_dto,
    question_orm_row_to_dto,
)


@dataclass
class ORMQuestionsService(IQuestionService):
    session: AsyncSession

    async def get_random(self, limit: int) -> list[QuestionDTO]:
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
        return await list_question_orm_row_to_dto(questions)

    async def get(self, pk: int) -> QuestionDTO:
        query = (
            select(Question)
            .where(Question.id == pk)
            .options(selectinload(Question.answers))
        )
        result = await self.session.execute(query)
        orm_result = result.fetchone()
        return await question_orm_row_to_dto(orm_result[0])


@dataclass
class ORMComplaintService(IComplaintService):
    session: AsyncSession

    async def create_complaint(
        self,
        text: str,
        question: QuestionDTO,
        profile: ProfileDTO,
    ) -> ComplaintDTO:
        complaint = Complaint(
            profile_id=profile.id,
            question_id=question.id,
            text=text,
            created_at=datetime.datetime.now(),
            solved=False,
        )
        self.session.add(complaint)
        await self.session.flush()
        return await complaint_model_to_dto(complaint, question, profile)
