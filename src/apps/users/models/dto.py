from dataclasses import dataclass
from datetime import datetime
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
class LadderStatisticDTO(StatisticEntity):
    profile: ProfileEntity
    title: BestPlayerTitleEntity | None = None


@dataclass
class ProfileAdminDTO(ProfileEntity):
    def __init__(self, last_visit: datetime, complaints: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_visit = last_visit
        self.complaints = complaints
