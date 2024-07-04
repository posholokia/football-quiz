from copy import copy
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from core.api.schema import PaginationOut
from core.apps.users.dto import (
    ProfileDTO,
    StatisticDTO,
)
from core.apps.users.exceptions.profile import (
    AlreadyExistsProfile,
    DoesNotExistsProfile,
)
from core.apps.users.schema import SetStatisticsSchema
from core.apps.users.services.storage.base import (
    IProfileService,
    IStatisticService,
)
from core.apps.users.services.validator.profile import ProfileValidator


@dataclass
class ProfileActions:
    profile_repository: IProfileService
    statistic_repository: IStatisticService
    validator: ProfileValidator

    async def create(self, device_uuid: str) -> ProfileDTO:
        try:
            profile = await self.profile_repository.create(device_uuid)
            profile_pk = profile.id
            name = f"Игрок-{profile_pk}"
            profile = await self.profile_repository.patch(
                profile_pk, name=name
            )
            await self.statistic_repository.create(profile_pk)
            return profile

        except IntegrityError:
            raise AlreadyExistsProfile()

    async def get_by_id(self, pk: int) -> ProfileDTO:
        try:
            return await self.profile_repository.get_by_id(pk)
        except TypeError:
            raise DoesNotExistsProfile()

    async def patch_profile(self, pk: int, name: str) -> ProfileDTO:
        await self.validator.validate(name=name)
        profile = await self.profile_repository.patch(pk, name=name)
        return profile


@dataclass
class StatisticsActions:
    profile_repository: IProfileService
    repository: IStatisticService

    async def create(self, profile_pk: int) -> None:
        await self.repository.create(profile_pk)

    async def patch(
        self,
        pk: int,
        game_stat: SetStatisticsSchema,
    ) -> StatisticDTO:
        profile = await self.profile_repository.get_by_id(pk)
        # получаем текущую статистику игрока
        current_stat = await self.repository.get_by_id(profile.id)
        # получаем обновленную статистику в виде DTO,
        # место в рейтинге не меняем
        after_game_stat = await self._get_updated_statistic(
            current_stat, game_stat
        )
        # записываем обновленную статистику в БД
        new_stat = await self.repository.patch(after_game_stat)
        # получаем новое место игрока после обновления статистики
        new_place = await self.repository.get_user_rank(profile.id)
        # если место не изменилось, выходим из функции
        if current_stat.place == new_place:
            return new_stat
        # получаем список всех игроков, которых обошли в рейтинге
        changed_place_stats = await self.repository.get_replaced_users(
            current_stat.place, new_place
        )
        # обновляем места игроков
        updated_stats, current_profile = await self._get_updated_places(
            changed_place_stats,
            new_place,
        )
        # записываем в БД смещенных игроков
        for stat in updated_stats:
            await self.repository.patch(stat)
        # записываем в БД текущего игрока
        profile_stat = await self.repository.patch(current_profile)
        return profile_stat

    async def get_by_id(self, pk: int) -> StatisticDTO:
        return await self.repository.get_by_id(pk)

    @staticmethod
    async def _get_updated_places(
        statistics: list[StatisticDTO],
        new_place: int,
    ) -> tuple[list[StatisticDTO], StatisticDTO]:
        """
        Обновление игровых мест в ладдере
        """
        stats = statistics.copy()
        # сортируем в обратном порядке по местам, так как
        # обновление в бд должно идти с конца на свободные места
        stats.sort(key=lambda x: x.place, reverse=True)
        # ставим ему временное значение места = 0, чтобы
        # следующий профиль смог занять его место
        stats[0].place = 0
        # делаем копию статистики игрока и присваиваем туда новое место
        stat_copy = copy(stats[0])
        stat_copy.place = new_place
        # смещаем всех игроков кроме поднимаемого
        for s in stats[1:]:
            s.place += 1
        return stats, stat_copy

    async def _get_updated_statistic(
        self,
        current_stat: StatisticDTO,
        game_stat: SetStatisticsSchema,
    ) -> StatisticDTO:
        return StatisticDTO(
            id=current_stat.id,
            games=current_stat.games + 1,
            score=current_stat.score + game_stat.score,
            place=current_stat.place,
            rights=current_stat.rights + game_stat.rights,
            wrongs=current_stat.wrongs + game_stat.wrongs,
            profile_id=current_stat.profile_id,
        )

    async def get_top_ladder(
        self, offset: int = 0, limit: int = 60,
    ) -> tuple[list[StatisticDTO], PaginationOut]:
        statistics = await self.repository.get_top_gamers(
            offset, limit
        )
        total = self.repository.get_count()
        paginator = PaginationOut(
            offset=offset,
            limit=limit,
            total=total,
        )
        return statistics, paginator

    async def get_count_statistic(self) -> int:
        return await self.repository.get_count()

    async def get_user_rank(self, pk: int) -> tuple[list[StatisticDTO], PaginationOut]:
        profile = await self.profile_repository.get_by_id(pk)
        rank = await self.repository.get_user_rank(profile.id)
        offset = 0 if rank <= 30 else rank - 30
        limit = 60
        total = await self.repository.get_count()
        statistics = await self.repository.get_top_gamers(offset, limit)
        paginator = PaginationOut(
            offset=offset,
            limit=limit,
            total=total,
        )
        return statistics, paginator
