from abc import ABC
from dataclasses import dataclass
from typing import overload

from apps.game_settings.models import GameSettingsEntity
from core.database.repository.base import IRepository


@dataclass
class IGameSettingsService(IRepository, ABC):
    @overload
    async def get_one(self) -> GameSettingsEntity:  # noqa
        """
        Получить настройки игры. Настройки
        могут быть только в единственном экземпляре.

        :return: Настройки.
        """

    @overload
    async def update(self, **fields) -> GameSettingsEntity:  # noqa
        """
        Обновить настройки игры.

        :param fields:  аттрибуты для обновления:
                        time_round, question_limit, max_energy, start_energy,
                        energy_for_ad, round_cost, question_skip_cost,
                        energy_perfect_round, recovery_period,
                        recovery_value, right_ratio, wrong_ratio.
        :return:        Настройки.
        """
