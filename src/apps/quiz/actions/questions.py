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
    __repository: IQuestionService
    __answer_repository: IAnswerService
    __answer_validator: AnswerListValidator
    transaction: Transaction

    async def get_random(self, limit: int) -> list[QuestionEntity]:
        """
        Получить случайные вопросы.

        :param limit:   Кол-во вопросов.
        :return:        Список вопросов.
        """
        return await self.__repository.get_random(limit)

    async def get_by_id(self, pk: int) -> QuestionEntity:
        """
        Получить вопрос по id.

        :param pk:  ID вопроса.
        :return:    Вопрос.
        """
        question = await self.__repository.get_one(id=pk)
        if not question:
            raise QuestionDoesNotExists()
        return question

    async def get_with_complaints(self, pk: int) -> QuestionEntity:
        """
        Получить вопрос по id вместе с жалобами.

        :param pk:  ID вопроса.
        :return:    Вопрос.
        """
        question = await self.__repository.get_one_with_complaints(id=pk)
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
        question_list = await self.__repository.get_list_with_complaints_count(
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
        return await self.__repository.get_count(search)

    async def delete_question(self, pk: int) -> None:
        """
        Удалить вопрос.

        :param pk:  ID вопроса.
        :return:    None.
        """
        await self.__repository.delete(pk)

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
        async with self.transaction.begin():
            answer_dict: list[dict[str, str | bool]] = data["answers"]
            await self.__answer_validator.validate(answer_dict)

            question = await self.__repository.create(
                text=data["text"],
                published=data["published"],
            )
            answers_data: list[dict[str, Any]] = copy.copy(answer_dict)
            for answer in answers_data:
                answer["question_id"] = question.id
            answers = await self.__answer_repository.bulk_create(answers_data)
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
        async with self.transaction.begin():
            answer_dict: list[dict[str, Any]] = data["answers"]
            await self.__answer_validator.validate(answer_dict)

            question = await self.__repository.update(
                pk=data["id"],
                text=data["text"],
                published=data["published"],
            )
            await self.__answer_repository.bulk_update(answer_dict)
            return QuestionAdminDTO(
                id=question.id,
                text=question.text,
                published=question.published,
                complaints=data["complaints"],
                answers=[AnswerEntity(**answer) for answer in answer_dict],
            )

    async def bulk_create_question_with_answers(
        self,
        data: list[dict[str, Any]],
    ) -> None:
        """
        Массовое создание вопросов с ответами.

        :param data:    Список json'ов с данными для создания вопроса
                        и ответов. Каждый вопрос должен содержать text,
                        published, answers. Answers должен содержать
                        text, right, question_id.
        :return:        None
        """
        question_data = copy.deepcopy(data)
        # здесь по тексту вопроса храним его ответы
        question_answer: dict[str, Any] = {}

        for question_dict in question_data:
            # для создания вопроса ответы не нужны, убираем их из вопроса
            answer_dict: list[dict[str, Any]] = question_dict.pop("answers")
            await self.__answer_validator.validate(answer_dict)

            # и сохраняем в словарь, чтобы найти после создания вопроса.
            question_answer.update({question_dict["text"]: answer_dict})
        questions = await self.__repository.bulk_create(question_data)
        answers_data = []  # для хранения данных создания ответов.

        for question in questions:
            # находим ответы для созданного вопроса
            answer_data = question_answer.get(question.text)
            # и присваиваем им id вопроса
            for answer in answer_data:
                answer.update({"question_id": question.id})
            answers_data.extend(answer_data)

        await self.__answer_repository.bulk_create(answers_data)
