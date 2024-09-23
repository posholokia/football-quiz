from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Generic,
    overload,
    TypeVar,
)

from apps.users.models import (
    BestPlayerTitleEntity,
    ProfileEntity,
    StatisticEntity,
    UserEntity,
)
from core.database.db import Base
from core.database.repository.base import IRepository


TModel = TypeVar("TModel", bound=Base)


@dataclass
class IProfileService(IRepository, ABC):
    @overload
    async def create(self, **data) -> ProfileEntity:  # noqa
        """
        Создать профиль.

        :param data:    Данные для создания профиля. Обязательные аргументы:
                        name, device_uuid
        :return:        Профиль.
        """

    @overload
    async def get_or_create(self, **fields) -> ProfileEntity:  # noqa
        """
        Получить существующий профиль или создать, если он не существует.

        :param fields:  Данные для создания профиля. Обязательные аргументы:
                        name, device_uuid
        :return:        Профиль.
        """

    @overload
    async def update(self, pk, **fields) -> ProfileEntity:  # noqa
        """
        Обновить профиль пользователя.

        :param pk:      Идентификатор профиля.
        :param fields:  Данные для обновления профиля. Возможные аргументы:
                        name, last_visit.
        :return:        Профиль.
        """

    @abstractmethod
    async def get_one(self, **filter_by) -> ProfileEntity | None:  # noqa
        """
        Получить профиль.

        :param filter_by:   Данные для фильтрации (поиска) профиля.
                            id - уникально;
                            device_uuid - уникально;
                            user_id - уникально;
                            name.
        :return:            Профиль.
        """

    @overload
    async def get_count(self, search: str | None = None) -> int:  # noqa
        """
        Получить количество записей в БД.

        :param search:  Отфильтровать записи по имени профиля.
        :return:        Число записей.
        """

    @abstractmethod
    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[tuple[ProfileEntity, int]]:
        """
        Возвращает список профилей с числом оставленных жалоб на вопросы.

        :param offset:  С какой записи получить профили.
        :param limit:   Количество профилей в списке.
        :param search:  Отфильтровать профили по имени.
        :return:        Список кортежей из профиля и числа жалоб.
        """

    @abstractmethod
    async def get_with_complaints_count_by_id(
        self,
        pk: int,
    ) -> tuple[ProfileEntity, int]:
        """
        Возвращает профиль с числом оставленных жалоб на вопросы.

        :param pk:  Id профиля.
        :return:    Кортеж из профиля и числа жалоб.
        """


@dataclass
class IStatisticService(IRepository, ABC, Generic[TModel]):
    @overload
    async def create(self, **data) -> StatisticEntity:  # noqa
        """
        Создать статистику.

        :param data:    Данные для создания статистики.
                        Обязательные аргументы:
                        profile_id, place.
        :return:        Статистика.
        """

    @overload
    async def get_one(self, **filter_by) -> StatisticEntity | None:  # noqa
        """
        Получить статистику.

        :param filter_by:   Данные для фильтрации (поиска) статистики:
                            id - уникально;
                            place - уникально;
                            profile_id - уникально;
                            games, score, rights, wrongs,
                            trend, perfect_rounds.
        :return:            Статистика или None.
        """

    @overload
    async def update(self, pk: int, **fields) -> StatisticEntity:  # noqa
        """
        Обновить статистику пользователя.

        :param pk:      Идентификатор статистики.
        :param fields:  Данные для обновления статистики. Возможные аргументы:
                        games, score, place, rights, wrongs,
                        trend, perfect_rounds.
        :return:        Статистика.
        """

    @abstractmethod
    async def get_user_rank(self, profile_id: int) -> int:
        """
        Возвращает место в ладдере игрока на основе его текущих очков.

        :param profile_id:  Id профиля.
        :return:            Номер места.
        """

    @abstractmethod
    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[StatisticEntity]:
        """
        Возвращает топ ладдера, отсортированный по занимаемому месту.
        Профиль подгружается к статистике.

        :param offset:  С какого места получить список.
        :param limit:   Сколько записей получить.
        :return:        Список статистик.
        """

    @abstractmethod
    async def replace_profiles(self, new_place, old_place) -> None:
        """
        Смещает игроков в ладдере, когда игрок
        сместился на новое место после игры.

        :param new_place:   Новое место игрока (после игры).
        :param old_place:   Прежнее место игрока (до игры).
        :return:            None
        """

    @abstractmethod
    async def get_count_positive_score(self) -> int:
        """
        Возвращает число статистик с неотрицательными очками.
        """

    @abstractmethod
    async def down_place_negative_score(self) -> None:
        """
        Увеличивает на 1 место все статистики с отрицательными очками.
        Используется при вставке новой статистики с 0 очками в ладдер.
        """

    @abstractmethod
    async def delete_all_statistics(self) -> None:
        """
        Удаляет все записи из таблицы. Очищает ежедневную
        и ежемесячную статистику каждый день/месяц.
        """

    @abstractmethod
    async def get_profile_id(self, place: int) -> int | None:
        """
        Получить id связанного профиля.

        :param place:   Место в ладдере.
        :return:        Id профиля.
        """


@dataclass
class IProfileTitleService(IRepository, ABC):
    @overload
    async def get_one(self, **filter_by) -> BestPlayerTitleEntity:  # noqa
        """
        Получить записи о титулах лучшего игрока.
        Если в репозитории записей нет, вернет титулы со значениями 0.

        :param filter_by:   Данные для поиска: profile_id.
        :return:            Титулы лучшего игрока.
        """

    @overload
    async def get_or_create(self, **fields) -> BestPlayerTitleEntity:  # noqa
        """
        Получить существующие титулы или создать, если их не существует.

        :param fields:  Данные для поиска или создания.
                        Обязательно profile_id.
        :return:        Титулы лучшего игрока.
        """

    @overload
    async def update(  # noqa
        self, profile_id, **fields
    ) -> BestPlayerTitleEntity:
        """
        Обновить титулы игрока.

        :param profile_id:  Id профиля игрока
        :param fields:      Данные для обновления титулов.
                            Возможные аргументы:
                            best_of_the_day, best_of_the_month.
        :return: Титулы лучшего игрока.
        """


@dataclass
class IUserService(IRepository, ABC):
    @overload
    async def get_one(self, **filter_by) -> UserEntity:  # noqa
        """
        Получить юзера.

        :param filter_by: Аттрибуты для фильтрации юзера. Предпочтительно
                          использовать в полях для фильтрации хотя бы один
                          уникальный аргумент. Можно фильтровать по:
                          id - уникально,
                          username - уникально,
                          is_superuser,
                          is_active,
                          date_joined.
        :return: Юзер.
        """
