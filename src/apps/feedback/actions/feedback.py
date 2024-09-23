from dataclasses import dataclass

from apps.feedback.models.entity import FeedbackEntity
from apps.feedback.services.storage.base import IFeedbackService


@dataclass
class FeedbackAction:
    __repository: IFeedbackService

    async def leave_feedback(self, name: str, email: str, text: str) -> None:
        await self.__repository.create(name=name, email=email, text=text)

    async def review_feedback(self) -> list[FeedbackEntity]:
        return await self.__repository.get_list()
