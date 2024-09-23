from contextlib import asynccontextmanager
from dataclasses import (
    dataclass,
    field,
)
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


class DatabaseConnection:
    def __init__(self):
        db_engine = create_async_engine(
            settings.database_url,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=False,
            isolation_level="READ COMMITTED",
        )
        self._session = async_sessionmaker(
            bind=db_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        read_only_db_engine = create_async_engine(
            settings.database_url,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=False,
            isolation_level="AUTOCOMMIT",
        )
        self._read_only_session = async_sessionmaker(
            bind=read_only_db_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def get_session(self):
        return self._session

    def get_ro_session(self):
        return self._read_only_session


@dataclass
class Database:
    __connection: DatabaseConnection
    __in_transaction: bool = field(init=False, default=False)
    __session: AsyncSession | None = field(init=False, default=None)
    __ro_session: AsyncSession | None = field(init=False, default=None)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        if self.__session is None:
            self.__session = self.__connection.get_session()()
        try:
            yield self.__session
        except SQLAlchemyError:
            await self.__session.rollback()
            logger.opt(exception=True).error("Session error:\n")
            raise
        finally:
            if self.__in_transaction:
                await self.__session.flush()
            else:
                await self.__session.commit()
                await self.__session.close()

    @asynccontextmanager
    async def get_ro_session(self) -> AsyncGenerator[AsyncSession, Any]:
        if self.__ro_session is None:
            self.__ro_session = self.__connection.get_ro_session()()
        try:
            yield self.__ro_session
        except SQLAlchemyError:
            logger.opt(exception=True).error("Session error:\n")
            raise
        finally:
            if not self.__in_transaction:
                await self.__ro_session.close()

    @asynccontextmanager
    async def _transaction(self) -> AsyncGenerator[None, None]:
        """
        Контекстный менеджер начинает транзакцию.
        """
        if self.__in_transaction:
            raise RuntimeError("Repository already begun transaction")

        # Внутри транзакции сессия на запись и чтения должна быть одна,
        # чтобы можно было внутри транзакции читать изменения. Также для
        # удобства сессии созданы тут, чтобы избежать ошибки в finally блоке,
        # когда этот менеджер ловит exception, а сессия еще не была открыта
        # (например, при валидации данных перед их записью в репозиторий).
        self.__in_transaction = True
        self.__session = self.__ro_session = self.__connection.get_session()()
        try:
            yield
        except Exception as error:
            await self.__session.rollback()
            raise error
        finally:
            await self.__session.commit()
            await self.__session.close()
            self.__in_transaction = False


@dataclass
class Transaction:
    """
    Для запуска транзакции объект Database в
    атомарном кейсе должен быть одним.
    """

    __db: Database

    @asynccontextmanager
    async def begin(self) -> AsyncGenerator[None, None]:
        """
        Начинает транзакцию для всех используемых репозиториев.
        Коммит сессии будет после выхода из контекстного менеджера,
        внутри будет только флеш сессии.

        :return: Асинхронный генератор.
        """
        async with self.__db._transaction():  # noqa
            yield
