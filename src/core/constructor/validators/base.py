from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass


@dataclass
class BaseValidator(ABC):
    @abstractmethod
    async def validate(self, *args, **kwargs) -> None: ...
