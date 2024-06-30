from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel

from core.apps.mapper import PydanticMapper
from core.apps.users.dto.dto import ProfileDTO


class ProfileSchema(PydanticMapper, BaseModel):
    id: int
    name: Annotated[str | None, MaxLen(50)]


class UpdateProfileSchema(BaseModel):
    name: Annotated[str, MinLen(5), MaxLen(50)]


class SetStatisticsSchema(BaseModel):
    score: int
    rights: int
    wrongs: int


class GetStatisticsSchema(PydanticMapper, SetStatisticsSchema):
    id: int
    games: int
    place: int


class ApiKeySchema(BaseModel):
    api_key: str
