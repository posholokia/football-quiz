from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from apps.users.models import Statistic
from apps.users.schema import SetStatisticsSchema

from services.storage_service.dto import StatisticDTO


async def get_last_place(session: AsyncSession) -> int:
    query = select(func.count()).select_from(Statistic)
    res = await session.execute(query)
    return res.fetchone()[0] + 1


async def get_updated_statistic(
    current_stat: StatisticDTO, game_stat: SetStatisticsSchema
) -> StatisticDTO:
    return StatisticDTO(
        id=current_stat.id,
        games=current_stat.games + 1,
        score=current_stat.score + game_stat.score,
        place=current_stat.place,
        rights=current_stat.rights + game_stat.rights,
        wrongs=current_stat.wrongs + game_stat.wrongs,
        profile_id=current_stat.profile_id,
    )
