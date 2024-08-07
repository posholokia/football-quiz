from dataclasses import dataclass

from sqlalchemy import (
    exists,
    select,
    update,
)

from apps.quiz.converter import answer_orm_to_entity
from apps.quiz.models import (
    Answer,
    AnswerEntity,
)
from apps.quiz.services.storage.base import IAnswerService
from core.database.db import Database


@dataclass
class ORMAnswerService(IAnswerService):
    db: Database

    async def create(
        self,
        text: str,
        right: bool,
        question_id: int,
    ) -> AnswerEntity:
        async with self.db.get_session() as session:
            answer = Answer(
                text=text,
                right=right,
                question_id=question_id,
            )
            session.add(answer)
            return await answer_orm_to_entity(answer)

    async def update(
        self,
        pk: int,
        **fields,
    ) -> AnswerEntity:
        async with self.db.get_session() as session:
            query = update(Answer).where(Answer.id == pk).values(**fields)
            res = await session.execute(query)
            orm_result = res.fetchone()
            return await answer_orm_to_entity(orm_result[0])

    async def exists_by_id(self, pk: int) -> bool:
        async with self.db.get_ro_session() as session:
            query = select(exists().where(Answer.id == pk))
            return session.scalar(query)
