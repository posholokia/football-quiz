import random as python_random
from dataclasses import dataclass

from loguru import logger

from sqlalchemy import (
    insert,
    select,
    tablesample,
    true,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    aliased,
    joinedload,
    selectinload,
)
from sqlalchemy.sql.functions import (
    func,
    random,
)
from sqlalchemy.sql.selectable import Select

from apps.quiz.exceptions.question import QuestionIntegrityError
from apps.quiz.models import (
    Complaint,
    QuestionEntity,
)
from apps.quiz.services.storage.base import IQuestionService
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMQuestionsService(CommonRepository, IQuestionService):
    async def get_random(self, limit: int) -> list[QuestionEntity]:
        async with self._db.get_ro_session() as session:
            q = aliased(
                self.model, tablesample(self.model, func.bernoulli(0.2))
            )
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
            return [q.to_entity() for q in questions]

    async def get_one(self, **filter_by) -> QuestionEntity | None:
        async with self._db.get_ro_session() as session:
            query = (
                select(self.model)
                .filter_by(**filter_by)
                .options(selectinload(self.model.answers))
            )
            result = await session.execute(query)
            obj = result.scalar()
            return obj.to_entity() if obj else None

    async def get_one_with_complaints(
        self, **filter_by
    ) -> QuestionEntity | None:
        async with self._db.get_ro_session() as session:
            query = (
                select(self.model)
                .filter_by(**filter_by)
                .options(
                    selectinload(self.model.answers),
                    joinedload(self.model.complaints).joinedload(
                        Complaint.category
                    ),
                )
            )
            result = await session.execute(query)
            obj = result.scalar()
            return obj.to_entity() if obj else None

    async def get_one_with_complaints_count(
        self, **filter_by
    ) -> tuple[QuestionEntity, int]:
        async with self._db.get_ro_session() as session:
            query = self._select_complaints_count().filter_by(**filter_by)
            result = await session.execute(query)
            questions, count = result.fetchone()
            return questions.to_entity(), count

    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int = 100,
        search: str | None = None,
    ) -> list[tuple[QuestionEntity, int]]:
        async with self._db.get_ro_session() as session:
            query = self._select_complaints_count().offset(offset).limit(limit)

            if search is not None:
                query = query.filter(self.model.text.ilike(f"%{search}%"))

            result = await session.execute(query)
            questions = result.fetchall()
            return [(q.to_entity(), c) for q, c in questions]

    async def get_count(self, search: str | None = None) -> int:
        async with self._db.get_ro_session() as session:
            query = select(func.count(self.model.text))

            if search is not None:
                query = query.filter(self.model.text.ilike(f"%{search}%"))

            result = await session.execute(query)
            return result.scalar_one()

    async def bulk_create(
        self, data: list[dict[str, str]]
    ) -> list[QuestionEntity]:
        try:
            async with self._db.get_session() as session:
                query = insert(self.model).returning(self.model)
                result = await session.execute(query, data)
                orm_objs = result.scalars().all()
                return [obj.to_entity() for obj in orm_objs]
        except IntegrityError as e:
            logger.error(
                "Ошибка при создании вопросов: {}\nданные: {}",
                e,
                data,
            )
            raise QuestionIntegrityError()

    def _select_complaints_count(self) -> Select:
        subquery = (
            select(
                self.model.id,
                func.count(Complaint.id).label("complaints_count"),
            )
            .outerjoin(Complaint, Complaint.question_id == self.model.id)
            .group_by(self.model.id)
            .subquery()
        )

        query = (
            select(self.model, subquery.c.complaints_count)
            .outerjoin(
                subquery,
                subquery.c.id == self.model.id,  # type: ignore
            )
            .options(selectinload(self.model.answers))
        )
        return query
