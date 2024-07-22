import math

from core.apps.users.actions import StatisticsActions
from core.apps.users.exceptions.statistics import StatisticDoseNotExists


async def get_offset(action: StatisticsActions, pk: int, limit: int) -> int:
    """
    Функция определяет offset так, чтобы при выгрузке
    ладдера игрок был в середине
    """
    try:
        user_rank = await action.get_user_rank(pk)
        offset = (
            0
            if math.ceil(limit / 2) > user_rank
            else user_rank - math.ceil(limit / 2)
        )
        return offset
    except StatisticDoseNotExists:
        # если статистики игрока нет, возвращает топ ладдера с 1 места
        return 0
