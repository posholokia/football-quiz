from dataclasses import dataclass

from loguru import logger
from redis import asyncio as aioredis

from config import settings


@dataclass
class RedisPool:
    db_number: int

    async def connect(self):
        conn = aioredis.Redis(
            host=settings.redis_host,
            username=settings.redis_user,
            password=settings.redis_pass,
            port=settings.redis_port,
            db=self.db_number,
        )
        return conn

    async def set_exp_value(
        self,
        key: str,
        value: str | int,
        time_ex: int | None = None,
        timestamp_ex: int | None = None,
    ) -> None:
        conn = await self.connect()
        if not (time_ex or timestamp_ex):
            time_ex = 86400

        result: bool = await conn.set(
            name=key,
            value=value,
            ex=time_ex,
            exat=timestamp_ex,
        )
        if not result:
            logger.error(
                "Не удалось записать ключ в Redis: {}: {}",
                key,
                value,
            )

    async def get_value(self, key: str) -> str | None:
        redis = await self.connect()
        value: bytes = await redis.get(key)

        if value is None:
            return value

        return value.decode()
