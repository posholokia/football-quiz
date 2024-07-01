from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.game_settings.dto.dto import GameSettingsDTO


@dataclass
class IGameSettingsService(ABC):
    @abstractmethod
    async def get(self) -> GameSettingsDTO: ...
