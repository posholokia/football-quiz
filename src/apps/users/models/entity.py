from dataclasses import dataclass
from typing import Optional


@dataclass
class UserEntity:
    id: int
    password: str
    is_superuser: bool
    is_active: bool
    username: str
    profile: Optional["ProfileEntity"] = None


@dataclass
class StatisticEntity:
    id: int
    games: int
    score: int
    place: int
    rights: int
    wrongs: int
    trend: int
    perfect_rounds: int
    profile: Optional["ProfileEntity"] = None


@dataclass
class BestPlayerTitleEntity:
    best_of_the_day: int = 0
    best_of_the_month: int = 0


@dataclass
class ProfileEntity:
    id: int
    name: str
    device_uuid: str
    user: UserEntity | None = None
    statistic: StatisticEntity | None = None
    title: BestPlayerTitleEntity | None = None
