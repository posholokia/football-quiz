import os
from typing import (
    Type,
    TypeVar,
)

from dotenv import load_dotenv


load_dotenv()

T = TypeVar("T")


class ConfigBuilder:
    @classmethod
    def build_from_env(cls, config: Type[T]) -> T:
        attrs = {}
        for field in config.__annotations__.keys():
            attrs.update({field: os.getenv(field.upper())})
        return config(**attrs)
