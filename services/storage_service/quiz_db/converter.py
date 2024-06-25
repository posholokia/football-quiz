from typing import Sequence

from sqlalchemy.engine.row import Row

from apps.quiz.models import Complaint, Question
from services.storage_service.dto import (
    AnswerDTO,
    QuestionDTO, ComplaintDTO, ProfileDTO,
)


async def list_question_orm_row_to_dto(
    orm_result: Sequence[Question],
) -> list[QuestionDTO]:
    question_list = []
    for question in orm_result:
        q = await question_orm_row_to_dto(question)
        question_list.append(q)
    return question_list


async def question_orm_row_to_dto(
    orm_result: Question
) -> QuestionDTO:
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
    question = (
        QuestionDTO(
            id=orm_result.id,
            text=orm_result.text,
            published=orm_result.published,
            answers=answer_list,
        )
    )
    return question


async def complaint_model_to_dto(
        complaint: Complaint,
        question: QuestionDTO,
        profile: ProfileDTO,
) -> ComplaintDTO:
    return ComplaintDTO(
        id=complaint.id,
        text=complaint.text,
        created_at=complaint.created_at,
        solved=complaint.solved,
        question=question,
        profile=profile,
    )
