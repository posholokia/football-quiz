from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class BaseValidator(ABC):
    @abstractmethod
    async def validate(self, *args, **kwargs) -> None: ...
