from typing import Type

from api.search import Period

from fastapi import Query

from apps.users.models import (
    DayStatistic,
    MonthStatistic,
    Statistic,
)
from core.database.db import Base


async def get_statistic_model(
    period: Period = Query(default=Period.total),
) -> Type[Base]:
    if period == Period.total:
        return Statistic
    elif period == Period.day:
        return DayStatistic
    elif period == Period.month:
        return MonthStatistic
