from dataclasses import dataclass

from apps.game_settings.models import GameSettingsEntity
from apps.game_settings.services.storage.base import IGameSettingsService


@dataclass
class GameSettingsActions:
    __repository: IGameSettingsService

    async def get_settings(self) -> GameSettingsEntity:
        """
        Получить настройки игры.

        :return: Настройки.
        """
        return await self.__repository.get_one()

    async def edit_settings(self, **fields) -> GameSettingsEntity:
        """
        Редактировать настройки игры.

        :param fields:  Настройки, которые будут обновлены. Может быть:
                        time_round, question_limit, max_energy, start_energy,
                        energy_for_ad, round_cost, question_skip_cost,
                        energy_perfect_round, recovery_period,
                        recovery_value, right_ratio, wrong_ratio.
        :return:        Настройки.
        """
        return await self.__repository.update(**fields)
