from dataclasses import dataclass

from loguru import logger

from services.redis_pool.connection import RedisConnection


@dataclass
class RedisStorage:
    connection: RedisConnection

    async def set_exp_value(
        self,
        key: str,
        value: str | int,
        time_ex: int | None = None,
        timestamp_ex: int | None = None,
    ) -> None:
        conn = await self.connection.connect()
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
