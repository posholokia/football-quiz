import random as python_random
from dataclasses import dataclass

from sqlalchemy import (
    delete,
    exists,
    select,
    tablesample,
    true,
    update,
)
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.orm import joinedload

from sqlalchemy.sql.functions import (
    func,
    random,
)
from sqlalchemy.sql.selectable import Select

from apps.quiz.exceptions import QuestionDoesNotExists
from apps.quiz.exceptions.answer import AnswerDoesNotExists
from apps.quiz.models import (
    Answer,
    Complaint,
    Question, QuestionEntity,
)
from apps.quiz.services.storage.base import IQuestionService
from core.database.db import Database


@dataclass
class ORMQuestionsService(IQuestionService):
    db: Database

    async def get_random(self, limit: int) -> list[Question]:
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
            return questions

    async def get_by_id(self, pk: int) -> Question:
        async with self.db.get_ro_session() as session:
            query = (
                select(Question)
                .where(Question.id == pk)
                .options(selectinload(Question.answers))
            )
            result = await session.execute(query)
            orm_result = result.scalar()

            if orm_result is None:
                raise QuestionDoesNotExists()
            return orm_result

    async def get_question_with_all_complaints(self, pk: int) -> QuestionEntity:
        async with self.db.get_ro_session() as session:
            query = (
                select(Question)
                .where(Question.id == pk)
                .options(
                    joinedload(Question.answers),
                    joinedload(Question.complaints)
                    .joinedload(Complaint.category)
                )
            )
            result = await session.execute(query)
            orm_result = result.scalar()

            if orm_result is None:
                raise QuestionDoesNotExists()
            return orm_result.to_entity()

    async def get_by_id_with_complaints_count(
        self,
        pk: int,
    ) -> Row[Question, int]:
        async with self.db.get_ro_session() as session:
            query = self._sub_question_with_complaints_count().where(
                Question.id == pk
            )
            result = await session.execute(query)
            questions = result.fetchone()
            return questions

    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int = 100,
        search: str | None = None,
    ) -> list[Row[Question, int]]:
        async with self.db.get_ro_session() as session:
            query = (
                self._sub_question_with_complaints_count()
                .offset(offset)
                .limit(limit)
            )

            if search is not None:
                query = query.filter(Question.text.ilike(f"%{search}%"))

            result = await session.execute(query)
            questions = result.fetchall()
            return questions

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

    async def create(self, text: str, published: bool) -> Question:
        async with self.db.get_session() as session:
            question = Question(
                text=text,
                published=published,
            )
            session.add(question)
            return question

    async def create_from_json(
        self,
        question_text: str,
        question_published: bool,
        answers: list[dict[str, str | bool]],
    ) -> tuple[Question, list[Answer]]:
        async with self.db.get_session() as session:
            q = Question(
                text=question_text,
                published=question_published,
            )
            session.add(q)
            await session.flush()

            answer_models = []
            for answer in answers:
                answer = Answer(
                    text=answer["text"],
                    right=answer["right"],
                    question_id=q.id,
                )
                session.add(answer)
                answer_models.append(answer)
            await session.flush(answer_models)

            return q, answer_models

    async def update_from_json(
        self,
        question_id: int,
        question_text: str,
        question_published: bool,
        answers: list[dict[str, str | bool | int]],
    ) -> tuple[Question, list[Answer]]:
        async with self.db.get_session() as session:
            query_questions = (
                update(Question)
                .where(Question.id == question_id)
                .values(
                    text=question_text,
                    published=question_published,
                )
                .returning(Question)
            )
            result = await session.execute(query_questions)
            question = result.scalar()

            if question is None:
                await session.rollback()
                raise QuestionDoesNotExists(
                    detail=f"Вопрос с id={question_id} не существует"
                )

            answer_models = []
            for answer in answers:
                query_answer = (
                    update(Answer)
                    .where(Answer.id == answer["id"])
                    .values(text=answer["text"], right=answer["right"])
                    .returning(Answer)
                )
                result = await session.execute(query_answer)
                a = result.scalar()

                if a is None:
                    await session.rollback()
                    raise AnswerDoesNotExists(
                        detail=f"Ответ с id={answer['id']} не существует"
                    )

                answer_models.append(a)
            return question, answer_models

    async def exists_by_id(self, pk: int) -> bool:
        async with self.db.get_ro_session() as session:
            query = select(exists().where(Question.id == pk))
            return session.scalar(query)

    def _sub_question_with_complaints_count(self) -> Select:
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
        )
        return query
