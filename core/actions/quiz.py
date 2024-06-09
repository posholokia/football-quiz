from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from core.actions.mixins import ORMAlchemy
from services.storage_service.dto import QuestionDTO
from services.storage_service.quiz_db.interface import ORMQuestionsService


@dataclass
class QuestionsActions(ORMAlchemy):
    session: AsyncSession
    storage: ORMQuestionsService = ORMQuestionsService

    async def get(self, limit: int) -> list[QuestionDTO]:
        async with self.session.begin():
            return await self.storage.get_random(limit)
