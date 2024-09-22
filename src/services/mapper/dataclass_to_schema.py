from types import UnionType
from typing import (
    Any,
    Sequence,
    Type,
    TypeVar,
    Union,
)


TSchema = TypeVar("TSchema")


def dataclass_to_schema(schema: Type[TSchema], obj: Any) -> TSchema:
    """
    Функция конвертирует объекты dataclass в pydantic схему.
    Правила:
        1. В датаклассе должны быть все обязательные поля, которые есть
        в схеме и с таким же названием
        2. Поддерживает Union аннотации
        3. Работает с Optional[type]
        4. Работает с VarType:
            T = TypeVar("T")

            class ASchema(BaseModel):
                name: str

            class BSchema(BaseModel, Generic[T]):
                field_: T

            dataclass_to_schema(BSchema[ASchema], dataclass_obj)

        5. Поддерживает списки <list[Obj]> или <list[Obj1 | Obj2 | Obj3]> и вложенные объекты:
            class ASchema(BaseModel):
                name: str

            class BSchema(BaseModel):
                my_field: Optional[ASchema] = None

            class CSchema(BaseModel):
                optional_field: str | None = None
                list_field: list[BSchema] = Field(default_factory=list)

            dataclass_to_schema(CSchema, dataclass_obj)
    :param schema:  pydantic схема в которую нужно конвертировать.
    :param obj:     Объект dataclass.
    :return:        Конвертированный объект pydantic схемы.
    """
    attrs = {}
    if isinstance(schema, Sequence):
        for c in schema:
            try:
                return dataclass_to_schema(c, obj)
            except AttributeError:
                continue
        raise
    for field in schema.model_fields.keys():
        value = getattr(obj, field)
        sub_schema = schema.model_fields[field]
        field_type = _extract_field_type_schema(sub_schema.annotation)
        if (
            isinstance(value, Sequence)
            and len(value) > 0
            and hasattr(value[0], "__dataclass_fields__")
            and isinstance(field_type, Sequence)
        ):
            attrs[field] = []
            for v in value:
                for ft in field_type:
                    try:
                        attrs[field].append(dataclass_to_schema(ft, v))
                        break
                    except AttributeError:
                        continue

        elif hasattr(value, "__dataclass_fields__"):
            attrs[field] = dataclass_to_schema(field_type, value)
        else:
            attrs[field] = value
    return schema(**attrs)


def _extract_field_type_schema(field_type: Any) -> Any:
    if isinstance(field_type, UnionType):
        return field_type.__args__
    elif hasattr(field_type, "__origin__"):
        if field_type.__origin__ is list:
            field_type = field_type.__args__
            if isinstance(field_type[0], UnionType):
                field_type = field_type[0].__args__
            return field_type
        if field_type.__origin__ is Union:
            field_type = field_type.__args__
    return field_type
