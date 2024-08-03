from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class ITokenStorage(ABC):
    @abstractmethod
    async def set_token(
        self,
        key: str,
        value: str,
        expire: int | float,
        *args,
        **kwargs,
    ): ...

    @abstractmethod
    async def get_token(self, key: str, *args, **kwargs): ...
