from dataclasses import dataclass


@dataclass
class AnswerDTO:
    id: int
    text: str
    right: bool
    question_id: int


@dataclass
class QuestionDTO:
    id: int
    text: str
    published: bool
    answers: list[AnswerDTO]


