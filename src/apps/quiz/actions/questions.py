from dataclasses import dataclass
from typing import Any

from apps.quiz.models import (
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.quiz.services.storage.base import IQuestionService
from apps.quiz.validator.answers import AnswerListValidator


@dataclass
class QuestionsActions:
    repository: IQuestionService
    answer_validator: AnswerListValidator

    async def get_random(self, limit: int) -> list[QuestionEntity]:
        questions = await self.repository.get_random(limit)
        return [q.to_entity() for q in questions]

    async def get(self, pk: int) -> QuestionEntity:
        question = await self.repository.get_by_id(pk)
        return question.to_entity()

    async def get_list(
        self,
        page: int,
        limit: int,
        search: str | None = None,
    ) -> list[QuestionAdminDTO]:
        offset = (page - 1) * limit
        question_list = await self.repository.get_list_with_complaints_count(
            offset, limit, search
        )
        return [
            QuestionAdminDTO(
                id=question.to_entity().id,
                text=question.to_entity().text,
                published=question.to_entity().published,
                complaints=complaints,
                answers=question.to_entity().answers,
            )
            for question, complaints in question_list
        ]

    async def get_count(self, search: str | None = None) -> int:
        return await self.repository.get_count(search)

    async def delete_question(self, pk: int) -> None:
        await self.repository.delete(pk)

    async def create_question_with_answers(
        self,
        question_dict: dict[str, Any],
    ) -> QuestionAdminDTO:
        answers = question_dict["answers"]
        await self.answer_validator.validate(answers)
        question, answers = await self.repository.create_from_json(
            question_text=question_dict["text"],
            question_published=question_dict["published"],
            answers=answers,
        )
        return QuestionAdminDTO(
            id=question.to_entity().id,
            text=question.to_entity().text,
            published=question.to_entity().published,
            answers=[answer.to_entity() for answer in answers],
        )

    async def update_question_with_answers(
        self,
        question_dict: dict[str, Any],
    ) -> QuestionAdminDTO:
        answers = question_dict["answers"]
        await self.answer_validator.validate(answers)
        question, answers = await self.repository.update_from_json(
            question_id=question_dict["id"],
            question_text=question_dict["text"],
            question_published=question_dict["published"],
            answers=answers,
        )
        return QuestionAdminDTO(
            id=question.to_entity().id,
            text=question.to_entity().text,
            published=question.to_entity().published,
            complaints=question_dict["complaints"],
            answers=[answer.to_entity() for answer in answers],
        )
