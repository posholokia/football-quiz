from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Callable,
    Coroutine,
    TypeVar,
)

from core.api.schema import PaginationOut
from core.apps.users.schema import PaginationResponseSchema


LOR = TypeVar("LOR")
LOP = TypeVar("LOP")
LOS = TypeVar("LOS")


@dataclass
class BasePaginator(ABC):
    @abstractmethod
    async def paginate(self, func: Callable[[int, int], Coroutine]): ...


@dataclass
class LimitOffsetPaginator(BasePaginator):
    pagination: LOP
    repository: LOR
    schema: LOS

    async def paginate(
        self, func: Callable[[int, int], Coroutine]
    ) -> Callable[[int, int], Coroutine]:
        async def wrapper(
            offset: int | None, limit: int
        ) -> PaginationResponseSchema:
            res = await func(offset, limit)

            total = await self.repository.get_count()
            obj_list = [self.schema.from_dto(obj) for obj in res]
            return PaginationResponseSchema(
                items=obj_list,
                paginator=PaginationOut(
                    offset=self.pagination.offset,
                    limit=self.pagination.limit,
                    total=total,
                ),
            )

        return wrapper
