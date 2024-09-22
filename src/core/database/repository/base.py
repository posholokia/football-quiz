from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import TypeVar

from core.database.db import Base


TModel = TypeVar("TModel", bound=Base)


@dataclass
class IRepository(ABC):
    """
    Базовая абстракция репозитория, в которой реализованы основные
    часто используемые методы.
    Абстракции репозиториев конкретной модели также можно наследовать
    для перегрузки тайпинга и добавления докстрингов.
    """

    @abstractmethod
    async def create(self, **data): ...

    @abstractmethod
    async def get_count(self) -> int:
        """
        Получить количество записей в БД, без фильтрации.

        :return: число записей
        """

    @abstractmethod
    async def get_one(self, **filter_by): ...

    @abstractmethod
    async def get_list(self, **filter_by): ...

    @abstractmethod
    async def update(self, pk, **fields): ...

    @abstractmethod
    async def get_or_create(self, **fields): ...

    @abstractmethod
    async def exists(self, **filter_by) -> bool | None:
        """
        Проверить существует ли объект.

        :param filter_by:   Параметры для поиска объекта.
        :return:            True если существует, None если нет.
        """

    @abstractmethod
    async def delete(self, pk: int) -> None:
        """
        Удалить объект.

        :param pk:  ID объекта.
        :return:    None.
        """
