from typing import Type

from fastapi import Query

from core.api.search import Period
from core.apps.users.models import (
    DayStatistic,
    MonthStatistic,
    Statistic,
)
from core.config.database.db import Base


async def get_statistic_model(
    period: Period = Query(default=Period.total),
) -> Type[Base]:
    if period == Period.total:
        return Statistic
    elif period == Period.day:
        return DayStatistic
    elif period == Period.month:
        return MonthStatistic
