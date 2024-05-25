from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from mobile.users.models import Statistic


async def get_last_place(session: AsyncSession) -> int:
    query = select(func.count()).select_from(Statistic)
    res = await session.execute(query)
    return res.fetchone()[0] + 1
