from dataclasses import dataclass
from typing import Annotated

from annotated_types import MaxLen


@dataclass
class FeedbackEntity:
    name: str
    email: str
    text: Annotated[str, MaxLen(500)]
