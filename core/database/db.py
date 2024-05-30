from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from config.settings import DATABASE_URL


db_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = async_sessionmaker(
    bind=db_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_session() -> AsyncGenerator:
    """Dependency for getting async session"""
    yield SessionLocal()
