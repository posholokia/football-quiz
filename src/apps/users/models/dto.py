from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .entity import (
    BestPlayerTitleEntity,
    ProfileEntity,
    StatisticEntity,
    UserEntity,
)


class PeriodStatistic(Enum):
    day: str = "day"
    month: str = " month"


@dataclass
class StatisticDTO:
    id: int
    games: int
    score: int
    place: int
    rights: int
    wrongs: int
    trend: int
    perfect_rounds: int
    profile: ProfileEntity
    title: BestPlayerTitleEntity


@dataclass
class ProfileAdminDTO:
    id: int
    name: str
    device_uuid: str
    last_visit: datetime
    complaints: int
    user: UserEntity | None = None
    statistic: StatisticEntity | None = None
