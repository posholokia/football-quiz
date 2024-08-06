from dataclasses import dataclass

from apps.quiz.models import (
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.quiz.services.storage.base import IQuestionService


@dataclass
class QuestionsActions:
    repository: IQuestionService

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

    async def patch_with_answers(
        self, pk: int, **fields
    ) -> QuestionEntity: ...
