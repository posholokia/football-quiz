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
    complaints: int = Field(default=0)
    answers: list[AnswerAdminRetrieveSchema] = Field(default_factory=list)


class QuestionFullCreateSchema(BaseModel):
    text: str
    published: bool
    answers: list[AnswerAdminBaseSchema]


class QuestionFullUpdateSchema(QuestionAdminRetrieveSchema):
    pass


class QuestionWithRelationshipsSchema(QuestionAdminRetrieveSchema):
    complaints: list["ComplaintShortRetrieveSchema"] = Field(
        default_factory=list
    )


class ProfileShortRetrieveSchema(BaseModel):
    id: int
    name: str


class QuestionShortAdminRetrieveSchema(BaseModel):
    id: int
    text: str


class CategoryAdminRetrieveSchema(BaseModel):
    id: int
    name: str


class ComplaintShortRetrieveSchema(BaseModel):
    id: int
    text: str
    created_at: datetime
    category: CategoryAdminRetrieveSchema


class ComplaintAdminRetrieveSchema(ComplaintShortRetrieveSchema):
    profile: ProfileShortRetrieveSchema
    question: QuestionShortAdminRetrieveSchema
