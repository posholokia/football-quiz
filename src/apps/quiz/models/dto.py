from dataclasses import (
    dataclass,
    field,
)

from .entity import AnswerEntity


@dataclass
class QuestionAdminDTO:
    id: int
    text: str
    published: bool
    complaints: int = 0
    answers: list[AnswerEntity] = field(default_factory=list)
