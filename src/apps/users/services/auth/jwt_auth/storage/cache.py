from dataclasses import dataclass

from apps.users.services.auth.jwt_auth.storage.base import ITokenStorage
from services.redis_pool import RedisPool


@dataclass
class RedisTokenStorage(ITokenStorage):
    storage: RedisPool

    async def set_token(
        self, key: str, value: str, expire: int | float
    ) -> None:
        await self.storage.set_exp_value(
            key=key,
            value=value,
            timestamp_ex=round(expire),
        )

    async def get_token(self, key: str) -> str | None:
        return await self.storage.get_value(key)
