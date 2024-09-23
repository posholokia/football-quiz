import math
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass
from typing import (
    Callable,
    Generic,
    ParamSpec,
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


TAction = TypeVar("TAction")
T = TypeVar("T")
F_Spec = ParamSpec("F_Spec")
F_Return = TypeVar("F_Return")
F_Schema = TypeVar("F_Schema")


@dataclass
class BasePaginator(ABC):
    @abstractmethod
    async def paginate(
        self, func: Callable[F_Spec, F_Return]
    ) -> Callable[F_Spec, F_Schema]: ...


@dataclass
class LazyLoad(BasePaginator):
    pagination: PaginationIn
    action: TAction

    def paginate(
        self, func: Callable[F_Spec, F_Return]
    ) -> Callable[F_Spec, F_Schema]:
        async def wrapper(
            offset: int,
            limit: int,
        ) -> F_Schema:
            res = await func(offset, limit)
            total = await self.action.get_count_statistic()
            return PaginationResponseSchema(
                items=res,
                paginator=PaginationOut(
                    offset=self.pagination.offset,
                    limit=self.pagination.limit,
                    total=total,
                ),
            )

        return wrapper


@dataclass
class PagePaginator(BasePaginator, Generic[F_Schema]):
    pagination: PagePaginationIn
    action: TAction

    def paginate(
        self, func: Callable[F_Spec, F_Return]
    ) -> Callable[F_Spec, F_Schema]:
        async def wrapper(page: int, limit: int, *args, **kwargs) -> F_Schema:
            res = await func(page, limit, *args, **kwargs)

            count = await self.action.get_count(*args, **kwargs)
            total = math.ceil(count / limit)

            return PagePaginationResponseSchema(
                items=res,
                paginator=PagePaginationOut(
                    page=self.pagination.page,
                    limit=self.pagination.limit,
                    pages=total,
                ),
            )

        return wrapper
