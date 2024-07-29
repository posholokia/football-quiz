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
    PaginationOut,
    PaginationResponseSchema,
)

from services.mapper import (
    Mapper,
    S,
)


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
