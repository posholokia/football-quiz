from datetime import datetime

from pydantic import BaseModel

from apps.users.schema import ProfileSchema


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


class RetrieveComplaintSchema(BaseModel):
    id: int
    profile: ProfileSchema
    question: QuestionSchema
    text: str
    created_at: datetime
    solved: bool
