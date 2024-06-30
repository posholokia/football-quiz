from dataclasses import dataclass

from core.apps.quiz.dto import QuestionDTO
from core.apps.quiz.dto.dto import ComplaintDTO
from core.apps.quiz.services.storage.base import IQuestionService, IComplaintService
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

    async def create(
        self,
        text: str,
        question_id: int,
        token: str,
    ) -> ComplaintDTO:
        profile = await self.profile_repository.get_by_device(token)
        question = await self.question_repository.get_by_id(question_id)
        return await self.complaint_repository.create(
            text, question, profile,
        )
