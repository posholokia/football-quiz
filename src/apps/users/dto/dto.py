from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class PeriodStatistic(Enum):
    day: str = "day"
    month: str = " month"


@dataclass
class UserDTO:
    id: int
    username: str
    date_joined: datetime
    profile_id: int


@dataclass
class StatisticDTO:
    id: int
    games: int
    score: int
    place: int
    rights: int
    wrongs: int
    perfect_rounds: int
    trend: int
    profile_id: int


@dataclass
class TitleStatisticDTO(StatisticDTO):
    title: Optional["ProfileTitleDTO"] = None


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
    profile: "ProfileDTO"
    title: Optional["ProfileTitleDTO"] = None


@dataclass
class ProfileTitleDTO:
    best_of_the_day: int
    best_of_the_month: int


@dataclass
class ProfileDTO:
    id: int
    name: str
    device_uuid: str
    user_id: int | None
