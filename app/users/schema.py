from typing import Annotated
from annotated_types import MinLen, MaxLen

from pydantic import BaseModel, EmailStr, field_validator


class ProfileSchema(BaseModel):
    id: int
    name: Annotated[str | None, MaxLen(50)]
