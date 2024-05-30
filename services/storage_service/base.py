from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.users.schema import SetStatisticsSchema

from services.storage_service.dto import (
    ProfileDTO,
    QuestionDTO,
    StatisticDTO,
)


@dataclass
class IQuestionService(ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> QuestionDTO: ...


@dataclass
class IProfileService(ABC):
    @abstractmethod
    async def create_profile(self, device: str) -> ProfileDTO: ...

    @abstractmethod
    async def patch_profile(self, profile: ProfileDTO) -> ProfileDTO: ...

    @abstractmethod
    async def get_profile(self, pk: int) -> ProfileDTO: ...


@dataclass
class IStatisticService(ABC):
    @abstractmethod
    async def create_user_statistics(self, pk: int) -> None: ...

    @abstractmethod
    async def get_user_statistics(
        self,
        pk: int,
    ) -> StatisticDTO: ...

    @abstractmethod
    async def update_user_statistics(
        self,
        new_stat: StatisticDTO,
    ) -> StatisticDTO: ...

    @abstractmethod
    async def get_user_rank(
        self,
        game_stat: SetStatisticsSchema,
    ) -> int: ...

    @abstractmethod
    async def get_changed_statistic(
        self,
        current_place: int,
        new_place: int,
    ) -> list[StatisticDTO]: ...