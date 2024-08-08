from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.users.models import (
    BestPlayerTitleEntity,
    ProfileEntity,
    StatisticEntity,
    UserEntity,
)
from apps.users.models.dto import (
    LadderStatisticDTO,
    ProfileAdminDTO,
    TitleStatisticDTO,
)


@dataclass
class IProfileService(ABC):
    @abstractmethod
    async def create(self, device: str) -> ProfileEntity: ...

    @abstractmethod
    async def get_or_create(self, device: str) -> ProfileEntity: ...

    @abstractmethod
    async def patch(self, pk, **fields) -> ProfileEntity: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> ProfileEntity: ...

    @abstractmethod
    async def get_by_device(self, token: str) -> ProfileEntity: ...

    @abstractmethod
    async def exists_by_token(self, token: str) -> bool: ...

    @abstractmethod
    async def get_count(self, search: str | None = None) -> int: ...

    @abstractmethod
    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> list[ProfileAdminDTO]: ...


@dataclass
class IStatisticService(ABC):
    @abstractmethod
    async def create(self, pk: int, place: int) -> StatisticEntity: ...

    @abstractmethod
    async def get_by_profile(self, profile_pk: int) -> TitleStatisticDTO: ...

    @abstractmethod
    async def get_by_place(self, place: int) -> StatisticEntity | None: ...

    @abstractmethod
    async def get_or_create_by_profile(
        self, profile_pk: int
    ) -> StatisticEntity: ...

    @abstractmethod
    async def patch(self, pk: int, **fields) -> TitleStatisticDTO: ...

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
    ) -> list[LadderStatisticDTO]: ...

    @abstractmethod
    async def get_count(self) -> int: ...

    @abstractmethod
    async def replace_profiles(self, new_place, old_place) -> None: ...

    @abstractmethod
    async def get_count_positive_score(self) -> int: ...

    @abstractmethod
    async def down_place_negative_score(self) -> None: ...

    @abstractmethod
    async def clear_statistic(self) -> None: ...

    @abstractmethod
    async def delete_all_statistics(self) -> None: ...


@dataclass
class IProfileTitleService(ABC):
    @abstractmethod
    async def get_or_create_by_profile(
        self,
        profile_pk: int,
    ) -> BestPlayerTitleEntity: ...

    @abstractmethod
    async def patch(
        self, profile_pk: int, **fields
    ) -> BestPlayerTitleEntity: ...


@dataclass
class IUserService(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> UserEntity: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> UserEntity: ...
