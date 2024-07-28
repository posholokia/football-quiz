from dataclasses import dataclass

from core.apps.users.dto import (
    ProfileDTO,
    StatisticDTO,
)
from core.apps.users.dto.dto import LadderStatisticDTO
from core.apps.users.services.storage import (
    IProfileService,
    IStatisticService,
)
from core.apps.users.services.validator.profile import ProfileValidator


@dataclass
class ProfileActions:
    profile_repository: IProfileService
    statistic_repository: "CompositeStatisticAction"
    validator: ProfileValidator

    async def create(self, device_uuid: str) -> ProfileDTO:
        # создаем профиль
        profile = await self.profile_repository.create(device_uuid)
        profile_pk = profile.id

        name = f"Игрок-{profile_pk}"
        #  присваиваем профилю новое имя
        profile = await self.profile_repository.patch(profile_pk, name=name)

        # await self.statistic_repository.create(profile_pk)
        return profile

    async def get_by_id(self, pk: int) -> ProfileDTO:
        return await self.profile_repository.get_by_id(pk)

    async def get_by_device(self, device_uuid: str) -> ProfileDTO:
        return await self.profile_repository.get_by_device(device_uuid)

    async def patch_profile(self, pk: int, name: str) -> ProfileDTO:
        await self.validator.validate(name=name)
        profile = await self.profile_repository.patch(pk, name=name)
        return profile


@dataclass
class StatisticsActions:
    profile_repository: IProfileService
    repository: IStatisticService

    async def create(self, profile_pk: int) -> None:
        count = await self.repository.get_count_positive_score()
        place = count + 1
        await self.repository.create(profile_pk, place)
        await self.repository.down_place_negative_score()

    async def patch(
        self,
        profile_pk: int,
        score: int,
        rights: int,
        wrongs: int,
    ) -> StatisticDTO:
        profile = await self.profile_repository.get_by_id(profile_pk)
        # получаем текущую статистику игрока
        current_stat = await self.repository.get_or_create_by_profile(
            profile.id,
        )
        # получаем обновленную статистику в виде DTO,
        # место в рейтинге не меняем
        after_game_stat = await self._get_updated_statistic(
            current_stat,
            score,
            rights,
            wrongs,
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
            pk=after_game_stat.id,
            place=new_place,
            trend=current_stat.place - new_place,
        )

        return stat

    async def get_by_profile(self, profile_pk: int) -> StatisticDTO:
        return await self.repository.get_by_profile(profile_pk)

    @staticmethod
    async def _get_updated_statistic(
        current_stat: StatisticDTO,
        score: int,
        rights: int,
        wrongs: int,
    ) -> StatisticDTO:
        return StatisticDTO(
            id=current_stat.id,
            games=current_stat.games + 1,
            score=current_stat.score + score,
            place=current_stat.place,
            rights=current_stat.rights + rights,
            wrongs=current_stat.wrongs + wrongs,
            trend=0,
            profile_id=current_stat.profile_id,
        )

    async def get_top_ladder(
        self,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[LadderStatisticDTO]:
        statistics = await self.repository.get_top_gamers(offset, limit)
        return statistics

    async def get_count_statistic(self) -> int:
        return await self.repository.get_count()

    async def get_user_rank(self, pk: int) -> int:
        return await self.repository.get_user_rank(pk)


@dataclass
class CompositeStatisticAction:
    actions: list[StatisticsActions]

    async def create(self, profile_pk: int) -> None:
        for action in self.actions:
            await action.create(profile_pk)

    async def patch(
        self,
        profile_pk: int,
        score: int,
        rights: int,
        wrongs: int,
    ) -> None:
        for action in self.actions:
            await action.patch(
                profile_pk,
                score,
                rights,
                wrongs,
            )
