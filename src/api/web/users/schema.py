from typing import Optional

from pydantic import BaseModel


class BaseStatistic(BaseModel):
    score: int
    rights: int
    wrongs: int


class ProfileTitleRetrieveSchema(BaseModel):
    best_of_the_day: int
    best_of_the_month: int


class StatisticsRetrieveSchema(BaseStatistic):
    id: int
    games: int
    place: int
    perfect_rounds: int
    trend: int
    title: Optional[ProfileTitleRetrieveSchema] = None
