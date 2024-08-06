from typing import (
    Generic,
    TypeVar,
)

from pydantic import (
    BaseModel,
    Field,
)


T = TypeVar("T")


class PaginationIn(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=30, ge=1, le=200)


class PaginationOut(PaginationIn):
    total: int


class PaginationResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    paginator: PaginationOut


class PagePaginationIn(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=100, ge=1, le=300)


class PagePaginationOut(PagePaginationIn):
    total: int


class PagePaginationResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    paginator: PagePaginationOut
