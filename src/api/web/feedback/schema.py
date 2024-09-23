from typing import Annotated

from annotated_types import MaxLen
from pydantic import (
    BaseModel,
    EmailStr,
)


class FeedbackLeaveSchema(BaseModel):
    name: str
    email: EmailStr
    text: Annotated[str, MaxLen(500)]
