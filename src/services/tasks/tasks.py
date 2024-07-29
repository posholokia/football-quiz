import asyncio

from celery import shared_task
from loguru import logger
from punq import Container

from apps.users.actions import StatisticsActions
from apps.users.dto import PeriodStatistic
from apps.users.models import (
    DayStatistic,
    MonthStatistic,
)
from config.containers import get_container
from services.firebase.firebase import change_api_key


@shared_task(name="clear_day_statistic")
def clear_day_statistic() -> None:
    logger.debug("Очистка ежедневной статистики")
    container: Container = get_container()
    repository: StatisticsActions = container.resolve(
        StatisticsActions, model=DayStatistic
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        repository.delete_statistic(period=PeriodStatistic.day)
    )


@shared_task(name="clear_month_statistic")
def clear_month_statistic() -> None:
    logger.debug("Очистка ежемесячной статистики")
    container: Container = get_container()
    repository: StatisticsActions = container.resolve(
        StatisticsActions, model=MonthStatistic
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        repository.delete_statistic(period=PeriodStatistic.month)
    )


@shared_task(name="update_firebase_config")
def update_firebase_config() -> None:
    logger.debug("Обновление Firebase конфига")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(change_api_key())
