from pydantic import BaseModel


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


class RetrieveCategorySchema(BaseModel):
    id: int
    name: str
