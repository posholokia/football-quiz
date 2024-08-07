import random as python_random
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    delete,
    exists,
    select,
    tablesample,
    true,
    update,
)
from sqlalchemy.orm import (
    aliased,
    selectinload,
)
from sqlalchemy.sql.functions import (
    func,
    random,
)
from sqlalchemy.sql.selectable import Select

from apps.quiz.converter import (
    answer_orm_to_entity,
    category_orm_to_entity,
    complaint_orm_to_entity,
    list_category_orm_to_entity,
    list_orm_question_to_entity,
    question_from_json_to_dto,
    question_orm_to_admin_dto,
    question_orm_to_entity,
)
from apps.quiz.exceptions import (
    CategoryComplaintDoesNotExists,
    QuestionDoesNotExists,
)
from apps.quiz.exceptions.answer import AnswerDoesNotExists
from apps.quiz.models import (
    Answer,
    AnswerEntity,
    CategoryComplaint,
    CategoryComplaintEntity,
    Complaint,
    ComplaintEntity,
    Question,
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.quiz.services.storage.base import (
    IAnswerService,
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

    async def get_by_id_with_complaints_count(
        self,
        pk: int,
    ) -> QuestionAdminDTO:
        async with self.db.get_ro_session() as session:
            query = self._sub_question_with_complaints_count().where(
                Question.id == pk
            )
            result = await session.execute(query)
            questions = result.fetchone()
            return await question_orm_to_admin_dto(questions)

    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[QuestionAdminDTO]:
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

    async def create(self, text: str, published: bool) -> QuestionEntity:
        async with self.db.get_session() as session:
            question = Question(
                text=text,
                published=published,
            )
            session.add(question)
            return await question_orm_to_entity(question)

    async def create_from_json(
        self,
        question_text: str,
        question_published: bool,
        answers: list[dict[str, str | bool]],
    ) -> QuestionAdminDTO:
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

            return await question_from_json_to_dto(
                question=q, answers=answer_models
            )

    async def update_from_json(
        self,
        question_id: int,
        question_text: str,
        question_published: bool,
        question_complaints: int,
        answers: list[dict[str, str | bool | int]],
    ) -> QuestionAdminDTO:
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
            question = result.fetchone()

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
                a = result.fetchone()

                if a is None:
                    await session.rollback()
                    raise AnswerDoesNotExists(
                        detail=f"Ответ с id={answer['id']} не существует"
                    )

                answer_models.append(a[0])
            return await question_from_json_to_dto(
                question=question[0],
                answers=answer_models,
                complaints=question_complaints,
            )

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
