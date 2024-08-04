from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    password: str
    is_superuser: bool
    is_active: bool
    username: str


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


@dataclass
class BestPlayerTitleEntity:
    best_of_the_day: int
    best_of_the_month: int


@dataclass
class ProfileEntity:
    id: int
    name: str
    device_uuid: str
    user: UserEntity | None = None
    statistic: StatisticEntity | None = None
    title: BestPlayerTitleEntity | None = None
