import asyncio

from celery import shared_task
from loguru import logger
from punq import Container

from core.apps.users.models import (
    DayStatistic,
    MonthStatistic,
)
from core.apps.users.services.storage.base import IStatisticService
from core.apps.users.services.storage.sqla import ORMStatisticService
from core.config.containers import get_container
from core.services.firebase.firebase import change_api_key


@shared_task(name="clear_day_statistic")
def clear_day_statistic() -> None:
    logger.debug("Очистка ежедневной статистики")
    container: Container = get_container()
    repository: ORMStatisticService = container.resolve(
        IStatisticService, model=DayStatistic
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(repository.clear_statistic())


@shared_task(name="clear_month_statistic")
def clear_month_statistic() -> None:
    logger.debug("Очистка ежемесячной статистики")
    container: Container = get_container()
    repository: ORMStatisticService = container.resolve(
        IStatisticService, model=MonthStatistic
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(repository.clear_statistic())


@shared_task(name="update_firebase_config")
def update_firebase_config() -> None:
    logger.debug("Обновление Firebase конфига")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(change_api_key())
