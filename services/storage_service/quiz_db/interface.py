import random as python_random
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.sql.functions import random

from apps.quiz.models import Question
from services.storage_service.base import IQuestionService
from services.storage_service.dto import QuestionDTO
from services.storage_service.quiz_db.converter import list_question_orm_row_to_dto


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
