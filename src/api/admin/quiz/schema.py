from pydantic import (
    BaseModel,
    Field,
)


class AnswerAdminRetrieveSchema(BaseModel):
    id: int
    text: str
    right: bool


class QuestionAdminRetrieveSchema(BaseModel):
    id: int
    text: str
    published: bool
    answers: list["AnswerAdminRetrieveSchema"] = Field(default_factory=list)
