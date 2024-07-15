import asyncio

from celery import shared_task
from punq import Container

from core.apps.users.models import (
    DayStatistic,
    MonthStatistic,
)
from core.apps.users.services.storage.base import IStatisticService
from core.apps.users.services.storage.sqla import ORMStatisticService
from core.config.containers import get_container


@shared_task(name="clear_day_statistic")
def clear_day_statistic() -> None:
    container: Container = get_container()
    repository: ORMStatisticService = container.resolve(
        IStatisticService, model=DayStatistic
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(repository.clear_statistic())


@shared_task(name="clear_month_statistic")
def clear_month_statistic() -> None:
    container: Container = get_container()
    repository: ORMStatisticService = container.resolve(
        IStatisticService, model=MonthStatistic
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(repository.clear_statistic())
