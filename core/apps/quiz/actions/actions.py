from dataclasses import dataclass

from core.apps.quiz.dto import QuestionDTO
from core.apps.quiz.services.storage.base import IQuestionService


@dataclass
class QuestionsActions:
    repository: IQuestionService

    async def get_random(self, limit: int) -> list[QuestionDTO]:
        return await self.repository.get_random(limit)

    async def get(self, pk: int) -> QuestionDTO:
        return await self.repository.get(pk)


# @dataclass
# class ComplaintsActions:
#     session: AsyncSession
#     storage: ORMComplaintService = ORMComplaintService
#
#     async def create(
#         self,
#         text: str,
#         question_id: int,
#         token: str,
#     ) -> ComplaintDTO:
#         async with self.session.begin():
#             profile_actions = await ProfileActions.start_session(self.session)
#             profile = await profile_actions.get_device_profile(token)
#             question_actions = await QuestionsActions.start_session(
#                 self.session
#             )
#             question = await question_actions.get(question_id)
#             return await self.storage.create_complaint(
#                 text,
#                 question,
#                 profile,
#             )
