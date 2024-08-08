from dataclasses import dataclass

from apps.quiz.models import (
    CategoryComplaintEntity,
    ComplaintEntity,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.users.services.storage.base import IProfileService


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

    async def get_list(
        self,
        page: int,
        limit: int,
    ) -> list[ComplaintEntity]:
        offset = (page - 1) * limit
        return await self.complaint_repository.get_list(offset, limit)

    async def get_count(self) -> int:
        return await self.complaint_repository.get_count()

    async def delete_complaint(self, pk: int) -> None:
        await self.complaint_repository.delete(pk)


@dataclass
class CategoryComplaintsActions:
    category_repository: ICategoryComplaintService

    async def list(self) -> list[CategoryComplaintEntity]:
        return await self.category_repository.list()
