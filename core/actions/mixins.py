from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db import get_session


@dataclass
class ORMAlchemy:
    @classmethod
    async def start_session(cls, session: AsyncSession = None):
        if session is None:
            session = await get_session().asend(None)
        storage = cls.storage(session)
        return cls(session, storage)