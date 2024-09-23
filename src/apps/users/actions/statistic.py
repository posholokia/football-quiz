from dataclasses import dataclass
from typing import (
    Generic,
    TypeVar,
)

from apps.users.exceptions.profile import DoesNotExistsProfile
from apps.users.exceptions.statistics import StatisticDoseNotExists
from apps.users.models import (
    BestPlayerTitleEntity,
    PeriodStatistic,
    StatisticEntity,
)
from apps.users.services.storage import (
    IProfileService,
    IStatisticService,
)
from apps.users.services.storage.base import IProfileTitleService
from core.database.db import Transaction


T = TypeVar("T")


@dataclass
class StatisticsActions(Generic[T]):
    __profile_repository: IProfileService
    __repository: IStatisticService[T]
    __title_repository: IProfileTitleService
    transaction: Transaction

    async def _create(self, profile_id: int) -> StatisticEntity:
        """
        Создать статистику игрока. Статистика размещается с 0 параметрами
        на последнее место среди игроков с неотрицательными очками.

        :param profile_id:  ID профиля.
        :return:            Статистика.
        """
        count = await self.__repository.get_count_positive_score()
        place = count + 1
        statistic = await self.__repository.create(
            profile_id=profile_id, place=place
        )
        await self.__repository.down_place_negative_score()
        return statistic

    async def patch(
        self,
        profile_pk: int,
        score: int,
        rights: int,
        wrongs: int,
        perfect_round: bool,
    ) -> None:
        """
        Обновить статистику после раунда. Сценарий перемещает всех затронутых
        игроков на свои места в соответствии с набранными очками и играми.

        :param profile_pk:      ID профиля.
        :param score:           Набрано очков.
        :param rights:          Верных ответов.
        :param wrongs:          Неверных ответов.
        :param perfect_round:   Раунд без ошибок True/False.
        :return:                None.
        """
        if not await self.__profile_repository.exists(id=profile_pk):
            raise DoesNotExistsProfile()
        # получаем текущую статистику игрока
        statistic = await self.__repository.get_one(profile_id=profile_pk)

        if statistic is None:
            statistic = await self._create(profile_id=profile_pk)

        current_place = statistic.place
        statistic.play_round(
            score=score,
            rights=rights,
            wrongs=wrongs,
            perfect_round=perfect_round,
        )
        # записываем обновленную статистику в БД без изменения места
        await self.__repository.update(
            pk=statistic.id,
            games=statistic.games,
            score=statistic.score,
            rights=statistic.rights,
            wrongs=statistic.wrongs,
            perfect_rounds=statistic.perfect_rounds,
            trend=statistic.trend,
        )
        # получаем новое место игрока после обновления статистики
        new_place = await self.__repository.get_user_rank(profile_pk)
        # если место не изменилось, выходим из функции
        if current_place == new_place:
            return
        # сдвигаем всех затронутых игроков и
        # присваиваем новое место текущему игроку
        await self.__repository.replace_profiles(new_place, current_place)
        await self.__repository.update(
            pk=statistic.id,
            place=new_place,
            trend=current_place - new_place,
        )

    async def get_by_profile(
        self, profile_pk: int
    ) -> tuple[StatisticEntity, BestPlayerTitleEntity]:
        """
        Получить статистику и титулы по id профиля.

        :param profile_pk:  ID профиля.
        :return:            Статистика и титулы лучшего игрока.
        """
        stat = await self.__repository.get_one(profile_id=profile_pk)
        if stat is None:
            raise StatisticDoseNotExists(
                detail=f"Статистика для игрока с id: {profile_pk} не найдена"
            )
        title = await self.__title_repository.get_one(profile_id=profile_pk)
        return stat, title

    async def delete_statistic(self, period: PeriodStatistic) -> None:
        """
        Очистка ежемесячной и ежедневной статистики и
        фиксация первых мест в рейтинге на момент очистки.

        :param period:  За какой период очистить статистику, месячную/дневную.
        :return:        None.
        """
        async with self.transaction.begin():
            first_place_profile = await self.__repository.get_profile_id(
                place=1
            )
            if first_place_profile is None:
                return

            profile_title = await self.__title_repository.get_or_create(
                profile_id=first_place_profile
            )

            profile_title.take_best_title(period)

            await self.__title_repository.update(
                profile_id=first_place_profile,
                best_of_the_day=profile_title.best_of_the_day,
                best_of_the_month=profile_title.best_of_the_month,
            )
            await self.__repository.delete_all_statistics()

    async def get_top_ladder(
        self,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[StatisticEntity]:
        """
        Получить топ игроков.

        :param offset:  С какой строки (места) получить игроков.
        :param limit:   Сколько игроков получить.
        :return:        Список статистики игроков.
        """
        return await self.__repository.get_top_gamers(offset, limit)

    async def get_count_statistic(self) -> int:
        """
        Возвращает общее число игроков со статистикой.
        """
        return await self.__repository.get_count()

    async def get_user_rank(self, profile_id: int) -> int:
        """
        Возвращает ранг юзера в ладдере.

        :param profile_id:  ID профиля.
        :return:            Место в ладдере.
        """
        return await self.__repository.get_user_rank(profile_id)


@dataclass
class CompositeStatisticAction:
    actions: list[StatisticsActions]
    transaction: Transaction

    async def patch(
        self,
        profile_pk: int,
        score: int,
        rights: int,
        wrongs: int,
        perfect_round: bool,
    ) -> None:
        """
        Обновление статистики игрока сразу в 3-х таблицах
        (общая, дневная, месячная).

        :param profile_pk:      ID профиля.
        :param score:           Набрано очков.
        :param rights:          Верных ответов.
        :param wrongs:          Неверных ответов.
        :param perfect_round:   Раунд без ошибок True/False.
        :return:                None.
        """
        async with self.transaction.begin():
            for action in self.actions:
                await action.patch(
                    profile_pk, score, rights, wrongs, perfect_round
                )
