from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.actions.mixins import ORMAlchemy
from apps.api.actions.users import ProfileActions
from services.storage_service.dto import (
    ComplaintDTO,
    QuestionDTO,
)
from services.storage_service.quiz_db.interface import (
    ORMComplaintService,
    ORMQuestionsService,
)


@dataclass
class QuestionsActions(ORMAlchemy):
    session: AsyncSession
    storage: ORMQuestionsService = ORMQuestionsService

    async def get_random(self, limit: int) -> list[QuestionDTO]:
        return await self.storage.get_random(limit)

    async def get(self, pk: int) -> QuestionDTO:
        return await self.storage.get(pk)


@dataclass
class ComplaintsActions(ORMAlchemy):
    session: AsyncSession
    storage: ORMComplaintService = ORMComplaintService

    async def create(
        self,
        text: str,
        question_id: int,
        token: str,
    ) -> ComplaintDTO:
        async with self.session.begin():
            profile_actions = await ProfileActions.start_session(self.session)
            profile = await profile_actions.get_device_profile(token)
            question_actions = await QuestionsActions.start_session(
                self.session
            )
            question = await question_actions.get(question_id)
            return await self.storage.create_complaint(
                text,
                question,
                profile,
            )
