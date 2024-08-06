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
from loguru import logger

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
            offset: int | None, limit: int
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
        self, func: Callable[[int, int], Coroutine]
    ) -> Callable[[int, int], Coroutine]:
        async def wrapper(
            page: int | None, limit: int
        ) -> PagePaginationResponseSchema:
            res = await func(page, limit)

            count = await self.action.get_count()
            total = math.ceil(count / limit)
            logger.info(
                "Всего записей: {}, лимит на страницу: {}, всего страниц: {}",
                count,
                limit,
                total,
            )

            obj_list = [
                Mapper.dataclass_to_schema(self.schema, obj) for obj in res
            ]
            return PagePaginationResponseSchema(
                items=obj_list,
                paginator=PagePaginationOut(
                    page=self.pagination.page,
                    limit=self.pagination.limit,
                    total=total,
                ),
            )

        return wrapper
