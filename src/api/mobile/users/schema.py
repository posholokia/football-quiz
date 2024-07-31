from typing import (
    Annotated,
    Optional,
)

from annotated_types import (
    MaxLen,
    MinLen,
)
from pydantic import BaseModel


class ProfileSchema(BaseModel):
    id: int
    name: Annotated[str | None, MinLen(3), MaxLen(25)]


class UpdateProfileSchema(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(25)]


class BaseStatistic(BaseModel):
    score: int
    rights: int
    wrongs: int


class StatisticsUpdateSchema(BaseStatistic):
    perfect_round: bool


class ApiKeySchema(BaseModel):
    api_key: str


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


class LadderStatisticRetrieveSchema(StatisticsRetrieveSchema):
    profile: ProfileSchema
