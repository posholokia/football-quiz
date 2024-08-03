from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
)

from loguru import logger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from config import settings


Base = declarative_base()


class Database:
    def __init__(self):
        db_engine = create_async_engine(
            settings.database_url,
            pool_size=25,
            echo=True,
        )
        self._session = async_sessionmaker(
            bind=db_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        session: AsyncSession = self._session()
        try:
            logger.debug("Соединение с БД открыто")
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.commit()
            await session.close()
            logger.debug("Соединение с БД закрылось")
