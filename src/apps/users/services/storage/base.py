from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.users.models import (
    BestPlayerTitle,
    Profile,
    Statistic,
    User,
)


@dataclass
class IProfileService(ABC):
    @abstractmethod
    async def create(self, device: str) -> Profile: ...

    @abstractmethod
    async def get_or_create(self, device: str) -> Profile: ...

    @abstractmethod
    async def patch(self, pk, **fields) -> Profile: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> Profile: ...

    @abstractmethod
    async def get_by_device(self, token: str) -> Profile: ...

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
    ) -> list[tuple[Profile, int]]: ...

    @abstractmethod
    async def get_with_complaints_count_by_id(
        self,
        pk: int,
    ) -> tuple[Profile, int]: ...


@dataclass
class IStatisticService(ABC):
    @abstractmethod
    async def create(
        self,
        pk: int,
        place: int,
    ) -> Statistic: ...

    @abstractmethod
    async def get_by_profile(self, profile_pk: int) -> Statistic: ...

    @abstractmethod
    async def get_by_place(self, place: int) -> Statistic | None: ...

    @abstractmethod
    async def get_or_create_by_profile(self, profile_pk: int) -> Statistic: ...

    @abstractmethod
    async def patch(self, pk: int, **fields) -> Statistic: ...

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
    ) -> list[Statistic]: ...

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
    ) -> BestPlayerTitle: ...

    @abstractmethod
    async def patch(self, profile_pk: int, **fields) -> BestPlayerTitle: ...


@dataclass
class IUserService(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> User: ...
