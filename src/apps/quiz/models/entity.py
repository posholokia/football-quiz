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
    complaints: list["ComplaintEntity"] = field(default_factory=list)


@dataclass
class AnswerEntity:
    id: int
    text: str
    right: bool
    question: QuestionEntity | None = None


@dataclass
class CategoryComplaintEntity:
    id: int
    name: str
    complaints: list["ComplaintEntity"] = field(default_factory=list)


@dataclass
class ComplaintEntity:
    id: int
    text: str
    created_at: datetime
    solved: bool
    profile: ProfileEntity | None = None
    question: QuestionEntity | None = None
    category: CategoryComplaintEntity | None = None
