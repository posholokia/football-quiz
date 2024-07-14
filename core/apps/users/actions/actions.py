from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

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
            stat = await self.statistic_repository.create(profile_pk)
            new_place = await self.statistic_repository.get_user_rank(
                profile.id
            )
            await self.statistic_repository.patch(stat.id, place=new_place)
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
        profile_pk: int,
        game_stat: SetStatisticsSchema,
    ) -> StatisticDTO:
        profile = await self.profile_repository.get_by_id(profile_pk)
        # получаем текущую статистику игрока
        current_stat = await self.repository.get_by_id(profile.id)
        # получаем обновленную статистику в виде DTO,
        # место в рейтинге не меняем
        after_game_stat = await self._get_updated_statistic(
            current_stat, game_stat
        )
        # записываем обновленную статистику в БД без изменения места
        new_stat = await self.repository.patch(
            pk=after_game_stat.id,
            games=after_game_stat.games,
            score=after_game_stat.score,
            rights=after_game_stat.rights,
            wrongs=after_game_stat.wrongs,
            trend=after_game_stat.trend,
        )
        # получаем новое место игрока после обновления статистики
        new_place = await self.get_user_rank(profile.id)
        # если место не изменилось, выходим из функции
        if current_stat.place == new_place:
            return new_stat
        # сдвигаем всех затронутых игроков и
        # присваиваем новое место ткущему юзеру
        await self.repository.replace_profiles(new_place, current_stat.place)
        stat = await self.repository.patch(
            pk=after_game_stat.id, place=new_place
        )

        return stat

    async def get_by_id(self, pk: int) -> StatisticDTO:
        return await self.repository.get_by_id(pk)

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
            trend=0,
            profile_id=current_stat.profile_id,
        )

    async def get_top_ladder(
        self,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[StatisticDTO]:
        statistics = await self.repository.get_top_gamers(offset, limit)
        return statistics

    async def get_count_statistic(self) -> int:
        return await self.repository.get_count()

    async def get_user_rank(self, pk: int) -> int:
        return await self.repository.get_user_rank(pk)
