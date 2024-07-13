from datetime import datetime

from pydantic import BaseModel

from core.apps.users.schema import ProfileSchema


class AnswerSchema(BaseModel):
    id: int
    text: str
    right: bool


class QuestionSchema(BaseModel):
    id: int
    text: str
    answers: list[AnswerSchema]


class CreateComplaintSchema(BaseModel):
    text: str
    question: int
    category: int
    profile: int


class RetrieveComplaintSchema(BaseModel):
    id: int
    profile: ProfileSchema
    question: QuestionSchema
    text: str
    created_at: datetime
    solved: bool
    category: "RetrieveCategorySchema"


class RetrieveCategorySchema(BaseModel):
    id: int
    name: str
