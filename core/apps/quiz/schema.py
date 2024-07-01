from datetime import datetime
from typing import (
    Any,
    Type,
)

from pydantic import BaseModel

from core.apps.mapper import PydanticMapper
from core.apps.users.schema import ProfileSchema


class AnswerSchema(PydanticMapper, BaseModel):
    id: int
    text: str
    right: bool


class QuestionSchema(PydanticMapper, BaseModel):
    id: int
    text: str
    answers: list[AnswerSchema]

    @classmethod
    def from_dto(cls: Type["QuestionSchema"], obj: Any) -> "QuestionSchema":
        mapped_fields = dict()
        for attr in cls.model_fields.keys():
            value = getattr(obj, attr)
            if attr == "answers":
                value = [AnswerSchema.from_dto(answer) for answer in value]
            mapped_fields.update({attr: value})
        return cls(**mapped_fields)


class CreateComplaintSchema(BaseModel):
    text: str
    question: int


class RetrieveComplaintSchema(PydanticMapper, BaseModel):
    id: int
    profile: ProfileSchema
    question: QuestionSchema
    text: str
    created_at: datetime
    solved: bool

    @classmethod
    def from_dto(
        cls: Type["RetrieveComplaintSchema"], obj: Any
    ) -> "RetrieveComplaintSchema":
        mapped_fields = dict()
        for attr in cls.model_fields.keys():
            value = getattr(obj, attr)
            if attr == "profile":
                value = ProfileSchema.from_dto(value)
            elif attr == "question":
                value = QuestionSchema.from_dto(value)
            mapped_fields.update({attr: value})
        return cls(**mapped_fields)
