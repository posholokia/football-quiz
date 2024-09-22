import copy
from dataclasses import dataclass
from typing import Any

from apps.quiz.exceptions import QuestionDoesNotExists
from apps.quiz.models import (
    AnswerEntity,
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.quiz.services.storage.base import (
    IAnswerService,
    IQuestionService,
)
from apps.quiz.validator.answers import AnswerListValidator
from core.database.db import Transaction


@dataclass
class QuestionsActions:
    repository: IQuestionService
    answer_repository: IAnswerService
    answer_validator: AnswerListValidator
    transaction: Transaction

    async def get_random(self, limit: int) -> list[QuestionEntity]:
        """
        Получить случайные вопросы.

        :param limit:   Кол-во вопросов.
        :return:        Список вопросов.
        """
        return await self.repository.get_random(limit)

    async def get_by_id(self, pk: int) -> QuestionEntity:
        """
        Получить вопрос по id.

        :param pk:  ID вопроса.
        :return:    Вопрос.
        """
        question = await self.repository.get_one(id=pk)
        if not question:
            raise QuestionDoesNotExists()
        return question

    async def get_with_complaints(self, pk: int) -> QuestionEntity:
        """
        Получить вопрос по id вместе с жалобами.

        :param pk:  ID вопроса.
        :return:    Вопрос.
        """
        question = await self.repository.get_one_with_complaints(id=pk)
        if not question:
            raise QuestionDoesNotExists()
        return question

    async def get_list(
        self,
        page: int,
        limit: int,
        search: str | None = None,
    ) -> list[QuestionAdminDTO]:
        """
        Получить список вопросов с числом жалоб.

        :param page:    Номер страницы с жалобами.
        :param limit:   Кол-во вопросов на странице.
        :param search:  Поиск вопросов по тексту вопроса.
        :return:        Список вопросов с числом жалоб.
        """
        offset = (page - 1) * limit
        question_list = await self.repository.get_list_with_complaints_count(
            offset, limit, search
        )
        return [
            QuestionAdminDTO(
                id=question.id,
                text=question.text,
                published=question.published,
                complaints=complaints,
                answers=question.answers,
            )
            for question, complaints in question_list
        ]

    async def get_count(self, search: str | None = None) -> int:
        """
        Получить кол-во вопросов.

        :param search:  Поиск вопросов по тексту вопроса.
        :return:        Число вопросов.
        """
        return await self.repository.get_count(search)

    async def delete_question(self, pk: int) -> None:
        """
        Удалить вопрос.

        :param pk:  ID вопроса.
        :return:    None.
        """
        await self.repository.delete(pk)

    async def create_question_with_answers(
        self,
        data: dict[str, Any],
    ) -> QuestionAdminDTO:
        """
        Создание вопроса вместе с ответами.

        :param data:    Json с данными для создания вопроса и ответов.
                        Должен содержать text, published, answers.
                        Answers должен содержать text, right, question_id.
        :return:        Вопрос с числом жалоб.
        """
        answer_dict: list[dict[str, str | bool]] = data["answers"]
        await self.answer_validator.validate(answer_dict)

        async with self.transaction.begin():
            question = await self.repository.create(
                text=data["text"],
                published=data["published"],
            )
            answers_data: list[dict[str, Any]] = copy.copy(answer_dict)
            for answer in answers_data:
                answer["question_id"] = question.id
            answers = await self.answer_repository.bulk_create(answers_data)
            return QuestionAdminDTO(
                id=question.id,
                text=question.text,
                published=question.published,
                answers=[answer for answer in answers],
            )

    async def update_question_with_answers(
        self,
        data: dict[str, Any],
    ) -> QuestionAdminDTO:
        """
        Обновление вопроса вместе с ответами.

        :param data:    Json с данными для создания вопроса и ответов.
                        Должен содержать id, text, published, answers.
                        Answers должен содержать id, text, right, question_id.
        :return:        Вопрос с числом жалоб.
        """
        answer_dict: list[dict[str, Any]] = data["answers"]
        await self.answer_validator.validate(answer_dict)

        async with self.transaction.begin():
            question = await self.repository.update(
                pk=data["id"],
                text=data["text"],
                published=data["published"],
            )
            await self.answer_repository.bulk_update(answer_dict)
            return QuestionAdminDTO(
                id=question.id,
                text=question.text,
                published=question.published,
                complaints=data["complaints"],
                answers=[AnswerEntity(**answer) for answer in answer_dict],
            )
