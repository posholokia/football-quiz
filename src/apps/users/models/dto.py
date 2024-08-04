from dataclasses import dataclass
from enum import Enum

from .entity import (
    BestPlayerTitleEntity,
    ProfileEntity,
    StatisticEntity,
)


class PeriodStatistic(Enum):
    day: str = "day"
    month: str = " month"


@dataclass
class TitleStatisticDTO(StatisticEntity):
    title: BestPlayerTitleEntity | None = None


@dataclass
class LadderStatisticDTO:
    id: int
    games: int
    score: int
    place: int
    rights: int
    wrongs: int
    perfect_rounds: int
    trend: int
    profile: ProfileEntity
    title: BestPlayerTitleEntity | None = None
