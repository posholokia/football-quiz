from typing import (
    Any,
    Type,
    TypeVar,
)


T = TypeVar("T", bound="PydanticMapper")


class PydanticMapper:
    @classmethod
    def from_dto(cls: Type[T], obj: Any) -> T:
        mapped_fields = dict()
        for attr in cls.model_fields.keys():
            mapped_fields.update({attr: getattr(obj, attr)})
        return cls(**mapped_fields)
