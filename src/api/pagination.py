import math
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Callable,
    Coroutine,
    Type,
    TypeVar,
)

from api.schema import (
    PagePaginationIn,
    PagePaginationOut,
    PagePaginationResponseSchema,
    PaginationIn,
    PaginationOut,
    PaginationResponseSchema,
)

from services.mapper import (
    Mapper,
    TSchema,
)


TAction = TypeVar("TAction")


@dataclass
class BasePaginator(ABC):
    @abstractmethod
    async def paginate(self, func: Callable[[int, int], Coroutine]): ...


@dataclass
class LimitOffsetPaginator(BasePaginator):
    pagination: PaginationIn
    action: TAction
    schema: Type[TSchema]

    async def paginate(
        self, func: Callable[[int, int], Coroutine]
    ) -> Callable[[int, int], Coroutine]:
        async def wrapper(
            offset: int,
            limit: int,
        ) -> PaginationResponseSchema:
            res = await func(offset, limit)

            total = await self.action.get_count_statistic()
            obj_list = [
                Mapper.dataclass_to_schema(self.schema, obj) for obj in res
            ]
            return PaginationResponseSchema(
                items=obj_list,
                paginator=PaginationOut(
                    offset=self.pagination.offset,
                    limit=self.pagination.limit,
                    total=total,
                ),
            )

        return wrapper


@dataclass
class PagePaginator(BasePaginator):
    pagination: PagePaginationIn
    action: TAction
    schema: Type[TSchema]

    async def paginate(
        self, func: Callable[[int, int, str | None], Coroutine]
    ) -> Callable[[int, int, str | None], Coroutine]:
        async def wrapper(
            page: int,
            limit: int,
            search: str | None = None,
        ) -> PagePaginationResponseSchema:
            res = await func(page, limit, search)

            count = await self.action.get_count(search)
            total = math.ceil(count / limit)

            obj_list = [
                Mapper.dataclass_to_schema(self.schema, obj) for obj in res
            ]
            return PagePaginationResponseSchema(
                items=obj_list,
                paginator=PagePaginationOut(
                    page=self.pagination.page,
                    limit=self.pagination.limit,
                    pages=total,
                ),
            )

        return wrapper
