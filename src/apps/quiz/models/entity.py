from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from apps.users.models import ProfileEntity


@dataclass
class QuestionEntity:
    id: int
    text: str
    published: bool
    answers: list["AnswerEntity"] = field(default_factory=list)


@dataclass
class AnswerEntity:
    id: int
    text: str
    right: bool


@dataclass
class ComplaintEntity:
    id: int
    profile: ProfileEntity
    question: QuestionEntity
    text: str
    created_at: datetime
    solved: bool
    category: "CategoryComplaintEntity"


@dataclass
class CategoryComplaintEntity:
    id: int
    name: str
