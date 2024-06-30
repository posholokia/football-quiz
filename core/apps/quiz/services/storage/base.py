from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.apps.quiz.dto.dto import QuestionDTO


@dataclass
class IQuestionService(ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> list[QuestionDTO]: ...

    @abstractmethod
    async def get(self, pk: int) -> QuestionDTO: ...


# @dataclass
# class IComplaintService(ABC):
#     @abstractmethod
#     async def create_complaint(
#         self,
#         text: str,
#         question: int,
#         profile: int,
#     ) -> ComplaintDTO: ...