from typing import Annotated

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


class SetStatisticsSchema(BaseModel):
    score: int
    rights: int
    wrongs: int


class GetStatisticsSchema(SetStatisticsSchema):
    id: int
    games: int
    place: int
    trend: int
    profile_id: int


class ApiKeySchema(BaseModel):
    api_key: str


class RetrieveLadderSchema(BaseModel):
    id: int
    score: int
    rights: int
    wrongs: int
    games: int
    place: int
    trend: int
    profile: ProfileSchema
