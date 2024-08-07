from pydantic import (
    BaseModel,
    Field,
)


class AnswerAdminBaseSchema(BaseModel):
    text: str
    right: bool


class AnswerAdminRetrieveSchema(AnswerAdminBaseSchema):
    id: int
    text: str
    right: bool


class QuestionAdminRetrieveSchema(BaseModel):
    id: int
    text: str
    published: bool
    complaints: int
    answers: list["AnswerAdminRetrieveSchema"] = Field(default_factory=list)


class QuestionFullCreateSchema(BaseModel):
    text: str
    published: bool
    answers: list["AnswerAdminBaseSchema"]


class QuestionFullUpdateSchema(QuestionAdminRetrieveSchema):
    pass
