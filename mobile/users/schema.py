from typing import Annotated
from annotated_types import MaxLen

from pydantic import BaseModel


class ProfileSchema(BaseModel):
    id: int
    name: Annotated[str | None, MaxLen(50)]
