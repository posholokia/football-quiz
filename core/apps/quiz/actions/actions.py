from dataclasses import dataclass

from core.apps.quiz.dto import QuestionDTO
from core.apps.quiz.dto.dto import ComplaintDTO, CategoryComplaintDTO
from core.apps.quiz.services.storage.base import (
    IComplaintService,
    IQuestionService, ICategoryComplaintService,
)
from core.apps.users.services.storage.base import IProfileService


@dataclass
class QuestionsActions:
    repository: IQuestionService

    async def get_random(self, limit: int) -> list[QuestionDTO]:
        return await self.repository.get_random(limit)

    async def get(self, pk: int) -> QuestionDTO:
        return await self.repository.get_by_id(pk)


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
    ) -> ComplaintDTO:
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

    async def list(self) -> list[CategoryComplaintDTO]:
        return await self.category_repository.list()
