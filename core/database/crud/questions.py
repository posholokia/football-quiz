import random as python_random

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import random

from mobile.quiz.models import Question
from mobile.quiz.schema import QuestionSchema


@dataclass
class QuestionsCRUD:
    session: AsyncSession

    async def get(self, number: int) -> list[QuestionSchema]:
        async with self.session.begin():
            q = aliased(Question)

            query = (
                select(
                    q,
                )
                .filter(q.published == True)
                .order_by(random())
                .limit(number)
                .options(selectinload(q.answers))
            )
            result = await self.session.execute(query)
            questions = result.scalars().all()
            for question in questions:
                question.answers = sorted(
                    question.answers, key=lambda x: python_random.random()
                )

            return list(questions)
