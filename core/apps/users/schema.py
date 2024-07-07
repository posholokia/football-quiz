from typing import (
    Annotated,
    Generic,
    TypeVar,
)

from annotated_types import (
    MaxLen,
    MinLen,
)
from pydantic import BaseModel

from core.api.schema import PaginationOut
from core.apps.mapper import PydanticMapper


T = TypeVar("T")


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
    trend: int
    profile_id: int


class ApiKeySchema(BaseModel):
    api_key: str


class PaginationResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    paginator: PaginationOut
