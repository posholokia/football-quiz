from typing import Annotated

from annotated_types import MaxLen
from pydantic import (
    BaseModel,
    EmailStr,
)


class FeedbackRetrieveSchema(BaseModel):
    name: str
    email: EmailStr
    text: Annotated[str, MaxLen(500)]
