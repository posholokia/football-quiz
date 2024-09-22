from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class PeriodStatistic(Enum):
    day: str = "day"
    month: str = " month"


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

    def play_round(
        self, score: int, rights: int, wrongs: int, perfect_round: bool
    ) -> None:
        self.games += 1
        self.score += score
        self.rights += rights
        self.wrongs += wrongs
        self.perfect_rounds += int(perfect_round)
        self.trend = 0


@dataclass
class BestPlayerTitleEntity:
    best_of_the_day: int = 0
    best_of_the_month: int = 0

    def take_best_title(self, period: PeriodStatistic) -> None:
        if period == PeriodStatistic.day:
            self.best_of_the_day += 1
        elif period == PeriodStatistic.month:
            self.best_of_the_month += 1


@dataclass
class ProfileEntity:
    id: int
    name: str
    device_uuid: str
    last_visit: datetime
    user: UserEntity | None = None
    statistic: StatisticEntity | None = None
    title: BestPlayerTitleEntity | None = None
