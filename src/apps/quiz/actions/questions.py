from dataclasses import dataclass
from typing import Any

from apps.quiz.models import (
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.quiz.services.storage.base import (
    IAnswerService,
    IQuestionService,
)
from apps.quiz.validator.answers import AnswerListValidator


@dataclass
class QuestionsActions:
    repository: IQuestionService
    answer_repository: IAnswerService
    answer_validator: AnswerListValidator

    async def get_random(self, limit: int) -> list[QuestionEntity]:
        return await self.repository.get_random(limit)

    async def get(self, pk: int) -> QuestionEntity:
        return await self.repository.get_by_id(pk)

    async def get_list(
        self,
        page: int,
        limit: int,
        search: str | None = None,
    ) -> list[QuestionAdminDTO]:
        offset = (page - 1) * limit
        return await self.repository.get_list_with_complaints_count(
            offset, limit, search
        )

    async def get_count(self, search: str | None = None) -> int:
        return await self.repository.get_count(search)

    async def delete_question(self, pk: int) -> None:
        await self.repository.delete(pk)

    async def create_question_with_answers(
        self,
        question: dict[str, Any],
    ) -> QuestionAdminDTO:
        answers = question["answers"]
        await self.answer_validator.validate(answers)
        return await self.repository.create_from_json(
            question_text=question["text"],
            question_published=question["published"],
            answers=answers,
        )

    async def update_question_with_answers(
        self,
        question: dict[str, Any],
    ) -> QuestionAdminDTO:
        answers = question["answers"]
        await self.answer_validator.validate(answers)
        return await self.repository.update_from_json(
            question_id=question["id"],
            question_text=question["text"],
            question_complaints=question["complaints"],
            question_published=question["published"],
            answers=answers,
        )
