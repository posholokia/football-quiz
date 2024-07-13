from dataclasses import fields
from typing import (
    Any,
    Type,
    TypeVar,
)


S = TypeVar("S")


def dataclass_to_schema(schema: Type[S], obj: Any) -> S:
    attrs = {}
    for field in fields(obj):
        value = getattr(obj, field.name)
        if (
            isinstance(value, list)
            and len(value) > 0
            and hasattr(value[0], "__dataclass_fields__")
        ):
            sub_schema = schema.__annotations__[field.name].__args__[0]
            attrs[field.name] = [
                dataclass_to_schema(sub_schema, item) for item in value
            ]
        elif hasattr(value, "__dataclass_fields__"):
            sub_schema = schema.__annotations__[field.name]
            attrs[field.name] = dataclass_to_schema(sub_schema, value)
        else:
            attrs[field.name] = value
    return schema(**attrs)
