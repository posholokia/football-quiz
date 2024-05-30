from pydantic import BaseModel


class AnswerSchema(BaseModel):
    id: int
    text: str
    right: bool


class QuestionSchema(BaseModel):
    id: int
    text: str
    answers: list[AnswerSchema]
