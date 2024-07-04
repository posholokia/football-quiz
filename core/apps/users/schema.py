from typing import Annotated

from annotated_types import (
    MaxLen,
    MinLen,
)
from pydantic import BaseModel

from core.api.schema import PaginationOut
from core.apps.mapper import PydanticMapper


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


class PaginationStatisticSchema(BaseModel):
    items: list[GetStatisticsSchema]
    paginator: PaginationOut
