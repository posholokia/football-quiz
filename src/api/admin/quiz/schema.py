from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class AnswerAdminBaseSchema(BaseModel):
    text: str
    right: bool


class AnswerAdminRetrieveSchema(AnswerAdminBaseSchema):
    id: int


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


class ProfileAdminRetrieveSchema(BaseModel):
    id: int
    name: str


class QuestionShortAdminRetrieveSchema(BaseModel):
    id: int
    text: str


class CategoryAdminRetrieveSchema(BaseModel):
    id: int
    name: str


class ComplaintAdminRetrieveSchema(BaseModel):
    id: int
    profile: ProfileAdminRetrieveSchema
    question: QuestionShortAdminRetrieveSchema
    text: str
    created_at: datetime
    category: CategoryAdminRetrieveSchema
