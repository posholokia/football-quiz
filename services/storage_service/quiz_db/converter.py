from typing import Sequence

from sqlalchemy.engine.row import Row

from services.storage_service.dto import QuestionDTO, AnswerDTO


async def list_question_orm_row_to_dto(orm_result: Sequence[Row]) -> list[QuestionDTO]:
    question_list = []
    for question in orm_result:
        answer_list = []
        answers = question.answers
        for answer in answers:
            answer_list.append(
                AnswerDTO(
                    id=answer.id,
                    text=answer.text,
                    right=answer.right,
                    question_id=answer.question_id,
                )
            )
        question_list.append(
            QuestionDTO(
                id=question.id,
                text=question.text,
                published=question.published,
                answers=answer_list,
            )
        )
    return question_list
