from typing import Sequence

from core.apps.quiz.dto import (
    AnswerDTO,
    QuestionDTO,
)
from core.apps.quiz.dto.dto import ComplaintDTO
from core.apps.quiz.models import Question, Complaint
from core.apps.users.dto import ProfileDTO


async def list_question_orm_to_dto(
    orm_result: Sequence[Question],
) -> list[QuestionDTO]:
    question_list = []
    for question in orm_result:
        q = await question_orm_to_dto(question)
        question_list.append(q)
    return question_list


async def question_orm_to_dto(orm_result: Question) -> QuestionDTO:
    answer_list = []
    answers = orm_result.answers
    for answer in answers:
        answer_list.append(
            AnswerDTO(
                id=answer.id,
                text=answer.text,
                right=answer.right,
                question_id=answer.question_id,
            )
        )
    question = QuestionDTO(
        id=orm_result.id,
        text=orm_result.text,
        published=orm_result.published,
        answers=answer_list,
    )
    return question


async def complaint_orm_to_dto(
        orm_result: Complaint,
        question: QuestionDTO,
        profile: ProfileDTO,
) -> ComplaintDTO:
    return ComplaintDTO(
        id=orm_result.id,
        profile=profile,
        question=question,
        text=orm_result.text,
        created_at=orm_result.created_at,
        solved=orm_result.solved,
    )
