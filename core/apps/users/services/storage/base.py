from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.users.dto import (
    ProfileDTO,
    StatisticDTO,
)


@dataclass
class IProfileService(ABC):
    @abstractmethod
    async def create(self, device: str) -> ProfileDTO: ...

    @abstractmethod
    async def patch(self, pk, **kwargs) -> ProfileDTO: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> ProfileDTO: ...

    @abstractmethod
    async def get_by_device(self, token: str) -> ProfileDTO: ...


@dataclass
class IStatisticService(ABC):
    @abstractmethod
    async def create(self, pk: int) -> StatisticDTO: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> StatisticDTO: ...

    @abstractmethod
    async def patch(self, new_stat: StatisticDTO) -> StatisticDTO: ...

    @abstractmethod
    async def get_user_rank(
        self,
        profile_pk: int,
    ) -> int: ...

    @abstractmethod
    async def get_replaced_users(
        self,
        current_place: int,
        new_place: int,
    ) -> list[StatisticDTO]: ...

    @abstractmethod
    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[StatisticDTO]: ...

    @abstractmethod
    async def get_count(self) -> int: ...
