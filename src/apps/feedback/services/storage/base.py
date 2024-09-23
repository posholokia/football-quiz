from abc import ABC
from dataclasses import dataclass
from typing import overload

from apps.feedback.models.entity import FeedbackEntity
from core.database.repository.base import IRepository


@dataclass
class IFeedbackService(IRepository, ABC):
    @overload
    async def get_list(  # noqa
        self, offset: int = 0, limit: int = 100
    ) -> list[FeedbackEntity]:
        """
        Получить список фидбеков.

        :param offset:  С какого объекта получить список.
        :param limit:   Кол-во объектов.
        :return:        Список фидбеков.
        """
