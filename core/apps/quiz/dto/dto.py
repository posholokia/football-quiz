from dataclasses import dataclass
from datetime import datetime

from core.apps.users.dto import ProfileDTO


@dataclass
class AnswerDTO:
    id: int
    text: str
    right: bool
    question_id: int


@dataclass
class QuestionDTO:
    id: int
    text: str
    published: bool
    answers: list[AnswerDTO]


@dataclass
class ComplaintDTO:
    id: int
    profile: ProfileDTO
    question: QuestionDTO
    text: str
    created_at: datetime
    solved: bool
