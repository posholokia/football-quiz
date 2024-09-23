from dataclasses import dataclass

from sqlalchemy import select

from apps.feedback.models.entity import FeedbackEntity
from apps.feedback.services.storage.base import IFeedbackService
from core.database.repository.sqla import CommonRepository


@dataclass
class ORMFeedbackService(CommonRepository, IFeedbackService):
    async def get_list(
        self, offset: int = 0, limit: int = 100
    ) -> list[FeedbackEntity]:
        async with self._db.get_ro_session() as session:
            query = select(self.model).offset(offset).limit(limit)
            results = await session.execute(query)
            obj_list = results.scalars().all()
            return [obj.to_entity() for obj in obj_list]
