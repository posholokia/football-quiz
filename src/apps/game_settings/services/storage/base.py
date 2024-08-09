from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.game_settings.models import GameSettings


@dataclass
class IGameSettingsService(ABC):
    @abstractmethod
    async def get(self) -> GameSettings: ...

    @abstractmethod
    async def patch(self, **fields) -> GameSettings: ...
