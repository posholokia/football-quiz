from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.game_settings.models import GameSettingsEntity


@dataclass
class IGameSettingsService(ABC):
    @abstractmethod
    async def get(self) -> GameSettingsEntity: ...

    @abstractmethod
    async def patch(self, **fields) -> GameSettingsEntity: ...
