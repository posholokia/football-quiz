from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.apps.quiz.dto.dto import QuestionDTO, ComplaintDTO
from core.apps.users.dto import ProfileDTO


@dataclass
class IQuestionService(ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> list[QuestionDTO]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> QuestionDTO: ...


@dataclass
class IComplaintService(ABC):
    @abstractmethod
    async def create(
        self,
        text: str,
        question: QuestionDTO,
        profile: ProfileDTO,
    ) -> ComplaintDTO: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> ComplaintDTO: ...

    @abstractmethod
    async def list(self) -> ComplaintDTO: ...
