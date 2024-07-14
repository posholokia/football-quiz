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

from core.api.mapper import (
    dataclass_to_schema,
    S,
)
from core.api.schema import PaginationOut
from core.apps.users.schema import PaginationResponseSchema


R = TypeVar("R")
P = TypeVar("P")


@dataclass
class BasePaginator(ABC):
    @abstractmethod
    async def paginate(self, func: Callable[[int, int], Coroutine]): ...


@dataclass
class LimitOffsetPaginator(BasePaginator):
    pagination: P
    repository: R
    schema: Type[S]

    async def paginate(
        self, func: Callable[[int, int], Coroutine]
    ) -> Callable[[int, int], Coroutine]:
        async def wrapper(
            offset: int | None, limit: int
        ) -> PaginationResponseSchema:
            res = await func(offset, limit)

            total = await self.repository.get_count()
            obj_list = [dataclass_to_schema(self.schema, obj) for obj in res]
            return PaginationResponseSchema(
                items=obj_list,
                paginator=PaginationOut(
                    offset=self.pagination.offset,
                    limit=self.pagination.limit,
                    total=total,
                ),
            )

        return wrapper
