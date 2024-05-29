from typing import Annotated
from annotated_types import MaxLen

from pydantic import BaseModel


class ProfileSchema(BaseModel):
    id: int
    name: Annotated[str | None, MaxLen(50)]


class UpdateProfileSchema(BaseModel):
    name: Annotated[str | None, MaxLen(50)]


class SetStatisticsSchema(BaseModel):
    score: int
    rights: int
    wrongs: int


class GetStatisticsSchema(SetStatisticsSchema):
    id: int
    games: int
    place: int
