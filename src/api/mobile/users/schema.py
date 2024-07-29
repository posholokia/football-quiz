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
    name: Annotated[str, MinLen(5), MaxLen(50)]


class StatisticsUpdateSchema(BaseModel):
    score: int
    rights: int
    wrongs: int


class ApiKeySchema(BaseModel):
    api_key: str


class ProfileTitleRetrieveSchema(BaseModel):
    best_of_the_day: int
    best_of_the_month: int


class StatisticsRetrieveSchema(StatisticsUpdateSchema):
    id: int
    games: int
    place: int
    trend: int
    title: Optional[ProfileTitleRetrieveSchema] = None


class LadderStatisticRetrieveSchema(BaseModel):
    id: int
    games: int
    score: int
    rights: int
    wrongs: int
    place: int
    trend: int
    profile: ProfileSchema
    title: Optional[ProfileTitleRetrieveSchema] = None
