from typing import Generator

from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.settings import DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_session() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = SessionLocal()
        yield session
    finally:
        await session.close()
