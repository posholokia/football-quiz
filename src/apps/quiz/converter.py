from typing import Sequence

from sqlalchemy.engine.row import Row

from apps.quiz.models import (
    Answer,
    AnswerEntity,
    CategoryComplaint,
    CategoryComplaintEntity,
    Complaint,
    ComplaintEntity,
    Question,
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.users.models import ProfileEntity


async def list_orm_question_to_entity(
    orm_result: Sequence[Question],
) -> list[QuestionEntity]:
    question_list = []
    for question in orm_result:
        q = await question_orm_to_entity(question)
        question_list.append(q)
    return question_list


async def question_orm_to_entity(orm_result: Question) -> QuestionEntity:
    answer_list = []
    answers = orm_result.answers
    for answer in answers:
        answer_list.append(
            AnswerEntity(
                id=answer.id,
                text=answer.text,
                right=answer.right,
            )
        )
    question = QuestionEntity(
        id=orm_result.id,
        text=orm_result.text,
        published=orm_result.published,
        answers=answer_list,
    )
    return question


async def created_from_json_question_to_dto(
    question: Question,
    answers: list[Answer],
):
    answer_list = [await answer_orm_to_entity(a) for a in answers]
    return QuestionAdminDTO(
        id=question.id,
        text=question.text,
        published=question.published,
        answers=answer_list,
        complaints=0,
    )


async def question_orm_to_admin_dto(orm_result: Row) -> QuestionAdminDTO:
    question, complaints_count = orm_result
    answer_list = [await answer_orm_to_entity(a) for a in question.answers]

    question = QuestionAdminDTO(
        id=question.id,
        text=question.text,
        published=question.published,
        answers=answer_list,
        complaints=complaints_count,
    )
    return question


async def answer_orm_to_entity(orm_result: Answer) -> AnswerEntity:
    return AnswerEntity(
        id=orm_result.id,
        text=orm_result.text,
        right=orm_result.right,
    )


async def complaint_orm_to_entity(
    orm_result: Complaint,
    question: QuestionEntity,
    profile: ProfileEntity,
    category: CategoryComplaintEntity,
) -> ComplaintEntity:
    return ComplaintEntity(
        id=orm_result.id,
        profile=profile,
        question=question,
        text=orm_result.text,
        created_at=orm_result.created_at,
        solved=orm_result.solved,
        category=category,
    )


async def category_orm_to_entity(
    orm_result: CategoryComplaint,
) -> CategoryComplaintEntity:
    return CategoryComplaintEntity(
        id=orm_result.id,
        name=orm_result.name,
    )


async def list_category_orm_to_entity(
    orm_result: Sequence[CategoryComplaint],
) -> list[CategoryComplaintEntity]:
    return [await category_orm_to_entity(cat) for cat in orm_result]
