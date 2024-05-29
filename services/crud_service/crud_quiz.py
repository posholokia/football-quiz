from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from services.crud_service.mixins import ORMAlchemy
from services.storage_service.dto import QuestionDTO
from services.storage_service.quiz_db.interface import ORMQuestionsService


@dataclass
class QuestionsCRUD(ORMAlchemy):
    session: AsyncSession
    storage: ORMQuestionsService = ORMQuestionsService

    async def get(self, limit: int) -> list[QuestionDTO]:
        return await self.storage.get_random(limit)
