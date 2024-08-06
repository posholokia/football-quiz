from dataclasses import dataclass

from apps.quiz.models import (
    CategoryComplaintEntity,
    ComplaintEntity,
    QuestionEntity,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.users.services.storage.base import IProfileService


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
    ) -> list[QuestionEntity]:
        offset = (page - 1) * limit
        return await self.repository.get_list(offset, limit, search)

    async def get_count(self, search: str | None = None) -> int:
        return await self.repository.get_count(search)


@dataclass
class ComplaintsActions:
    complaint_repository: IComplaintService
    profile_repository: IProfileService
    question_repository: IQuestionService
    category_repository: ICategoryComplaintService

    async def create(
        self,
        text: str,
        question_id: int,
        category_id: int,
        profile_id: int,
    ) -> ComplaintEntity:
        profile = await self.profile_repository.get_by_id(profile_id)
        question = await self.question_repository.get_by_id(question_id)
        category = await self.category_repository.get_by_id(category_id)

        return await self.complaint_repository.create(
            text,
            question,
            profile,
            category,
        )


@dataclass
class CategoryComplaintsActions:
    category_repository: ICategoryComplaintService

    async def list(self) -> list[CategoryComplaintEntity]:
        return await self.category_repository.list()
