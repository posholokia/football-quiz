from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.quiz.dto.dto import (
    CategoryComplaintDTO,
    ComplaintDTO,
    QuestionDTO,
)
from apps.users.dto import ProfileDTO


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
        category_id: CategoryComplaintDTO,
    ) -> ComplaintDTO: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> ComplaintDTO: ...

    @abstractmethod
    async def list(self) -> ComplaintDTO: ...


@dataclass
class ICategoryComplaintService(ABC):
    @abstractmethod
    async def list(self) -> list[CategoryComplaintDTO]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> CategoryComplaintDTO: ...
