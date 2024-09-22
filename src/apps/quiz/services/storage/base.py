from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import overload

from apps.quiz.models import (
    AnswerEntity,
    CategoryComplaintEntity,
    ComplaintEntity,
    QuestionEntity,
)
from core.database.repository.base import IRepository


@dataclass
class IQuestionService(IRepository, ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> list[QuestionEntity]:
        """
        Получить случайные вопросы.

        :param limit:   Сколько вопросов получить.
        :return:        Список вопросов.
        """

    @overload
    async def get_one(self, **filter_by) -> QuestionEntity | None:  # noqa
        """
        Получить один вопрос.

        :param filter_by:   Параметры для поиска вопроса.
                            Могут быть: id - уникально; text, published.
        :return:            Вопрос или None если вопрос не найден.
        """

    @abstractmethod
    async def get_one_with_complaints(
        self, **filter_by
    ) -> QuestionEntity | None:
        """
        Получить вопрос вместе с жалобами.

        :param filter_by:   Параметры для поиска вопроса.
                            Могут быть: id - уникально; text, published.
        :return:            Вопрос или None если вопрос не найден.
        """

    @abstractmethod
    async def get_one_with_complaints_count(
        self, **filter_by
    ) -> tuple[QuestionEntity, int]:
        """
        Получить вопрос вместе с количеством жалоб.

        :param filter_by:   Параметры для поиска вопроса.
                            Могут быть: id - уникально; text, published.
        :return:            Вопрос и число жалоб на него.
        """

    @abstractmethod
    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int = 100,
        search: str | None = None,
    ) -> list[tuple[QuestionEntity, int]]:
        """
        Получить список вопросом вместе с количеством жалоб.

        :param offset:  С какой записи получить вопросы.
        :param limit:   Сколько получить вопросов.
        :param search:  Поиск вопросов по тексту. Без учета
                        регистра и строгого соответветстия.
        :return:        Вопрос.
        """

    @overload
    async def get_count(self, search: str | None = None) -> int:  # noqa
        """
        Получить кол-во вопросов.

        :param search:  Поиск вопроса по тексту.
        :return:        Кол-во вопросов.
        """

    @overload
    async def create(self, **data) -> QuestionEntity:  # noqa
        """
        Создать вопрос.

        :param data:    Данные для создания вопроса - text, published.
        :return:        Вопрос.
        """

    @overload
    async def update(self, pk, **fields) -> QuestionEntity:  # noqa
        """
        Обновить вопрос.

        :param pk:      ID вопроса.
        :param fields:  Параметры которые необходимо обновить. Могут быть:
                        text, published.
        :return:        Вопрос.
        """


@dataclass
class IAnswerService(ABC):
    @abstractmethod
    async def bulk_create(
        self, data: list[dict[str, str]]
    ) -> list[AnswerEntity]:
        """
        Создать ответы на вопрос.

        :param data:    Данные для создания ответов. Передаются списком
                        из словарей, где ключи - имя аттрибутов ответа:
                        text, right, question_id.
        :return:        Ответы.
        """

    @abstractmethod
    async def bulk_update(self, data: list[dict[str, str]]) -> None:  # noqa
        """
        Обновить ответы.

        :param data:    Данные для обновления ответов. Передаются списком
                        из словарей, где ключи - имя аттрибутов ответа:
                        id, text, right. Обновление происходит по id,
                        поэтому он обязательно должен быть в словаре.
        :return:        None.
        """


@dataclass
class IComplaintService(IRepository, ABC):
    @overload
    async def create(self, **data) -> ComplaintEntity:  # noqa
        """
        Создать жалобу.

        :param data:    Данные для создания жалобы - text, question_id,
                        profile_id, category_id.
        :return:        Жалоба.
        """

    @overload
    async def get_one(self, **filter_by) -> ComplaintEntity:  # noqa
        """
        Получить одну жалобу.

        :param filter_by:   Параметры для поиска вопроса.
                            Могут быть: id - уникально; text, created_at,
                            solved.
        :return:            Вопрос или None если вопрос не найден.
        """

    @abstractmethod
    async def get_list(
        self, offset: int, limit: int = 100
    ) -> list[ComplaintEntity]:
        """
        Получить список жалоб.

        :param offset:  С какой записи получить жалобы.
        :param limit:   Количество жалоб.
        :return:        Список жалоб.
        """


@dataclass
class ICategoryComplaintService(IRepository, ABC):
    @abstractmethod
    async def list(self) -> list[CategoryComplaintEntity]:
        """
        Получить список категорий жалоб.

        :return: Список категорий.
        """
