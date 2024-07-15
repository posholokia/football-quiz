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
    async def get_or_create(self, device: str) -> ProfileDTO: ...

    @abstractmethod
    async def patch(self, pk, **kwargs) -> ProfileDTO: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> ProfileDTO: ...

    @abstractmethod
    async def get_by_device(self, token: str) -> ProfileDTO: ...


@dataclass
class IStatisticService(ABC):
    @abstractmethod
    async def create(self, pk: int, place: int) -> StatisticDTO: ...

    @abstractmethod
    async def get_by_profile(self, profile_pk: int) -> StatisticDTO: ...

    @abstractmethod
    async def patch(self, pk: int, **fields) -> StatisticDTO: ...

    @abstractmethod
    async def get_user_rank(
        self,
        profile_pk: int,
    ) -> int: ...

    @abstractmethod
    async def get_top_gamers(
        self,
        offset: int | None,
        limit: int | None,
    ) -> list[StatisticDTO]: ...

    @abstractmethod
    async def get_count(self) -> int: ...

    @abstractmethod
    async def replace_profiles(self, new_place, old_place) -> None: ...

    @abstractmethod
    async def get_count_positive_score(self) -> int: ...

    @abstractmethod
    async def down_place_negative_score(self) -> None: ...
