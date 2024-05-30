from copy import copy
from dataclasses import dataclass

from fastapi import HTTPException
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.exc import (
    IntegrityError,
    InvalidRequestError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.users.schema import SetStatisticsSchema

from services.storage_service.dto import (
    ProfileDTO,
    StatisticDTO,
)
from services.storage_service.user_db.interface import (
    ORMProfileService,
    ORMStatisticService,
)

from .mixins import ORMAlchemy
from .utils import get_updated_statistic


@dataclass
class ProfileCRUD(ORMAlchemy):
    session: AsyncSession
    storage: ORMProfileService = ORMProfileService

    async def create(self, device_uuid: str) -> ProfileDTO:
        try:
            profile = await self.storage.create_profile(device_uuid)
            name = f"Игрок-{profile.id}"
            profile = await self.storage.patch_profile(
                profile.id,
                name=name,
            )
            stat_crud = await StatisticsCRUD.start(self.session)
            await stat_crud.create(profile.id)

            return profile

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для этого устройства уже создан профиль",
            )
        except (InvalidRequestError, ResponseValidationError, TypeError):
            pass  # закинуть логи

    async def get(self, pk: int) -> ProfileDTO:
        try:
            profile = await self.storage.get_profile(pk)
            return profile
        except TypeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой профиль не найден",
            )

    async def get_device_profile(self, token: str) -> ProfileDTO:
        profile = await self.storage.get_device_profile(token)
        return profile

    async def patch(self, pk: int, **kwargs) -> ProfileDTO:
        try:
            profile = await self.storage.patch_profile(pk, **kwargs)
            return profile
        except TypeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой профиль не найден",
            )


@dataclass
class StatisticsCRUD(ORMAlchemy):
    session: AsyncSession
    storage: ORMStatisticService = ORMStatisticService

    async def create(self, pk: int) -> None:
        await self.storage.create_user_statistics(pk)

    async def patch(
        self,
        pk: int,
        game_stat: SetStatisticsSchema,
    ) -> StatisticDTO:
        current_stat = await self.storage.get_user_statistics(
            pk,
        )
        after_game_stat = await get_updated_statistic(current_stat, game_stat)
        new_stat = await self.storage.update_user_statistics(after_game_stat)

        new_place = await self.storage.get_user_rank(new_stat)
        if current_stat.place == new_place:
            return new_stat
        changed_place_stats = await self.storage.get_changed_statistic(
            current_stat.place, new_place
        )
        updated_stats, current_profile = await self.get_updated_places(
            changed_place_stats,
            new_place,
        )

        for stat in updated_stats:
            await self.storage.update_user_statistics(stat)

        profile_stat = await self.storage.update_user_statistics(
            current_profile
        )
        return profile_stat

    async def get_statistic(self, pk: int) -> StatisticDTO:
        return await self.storage.get_user_statistics(pk)

    @staticmethod
    async def get_updated_places(
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
