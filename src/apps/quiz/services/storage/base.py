from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.quiz.models import (
    CategoryComplaintEntity,
    ComplaintEntity,
    QuestionEntity,
)
from apps.users.models import ProfileEntity


@dataclass
class IQuestionService(ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> list[QuestionEntity]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> QuestionEntity: ...


@dataclass
class IComplaintService(ABC):
    @abstractmethod
    async def create(
        self,
        text: str,
        question: QuestionEntity,
        profile: ProfileEntity,
        category_id: CategoryComplaintEntity,
    ) -> ComplaintEntity: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> ComplaintEntity: ...

    @abstractmethod
    async def list(self) -> ComplaintEntity: ...


@dataclass
class ICategoryComplaintService(ABC):
    @abstractmethod
    async def list(self) -> list[CategoryComplaintEntity]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> CategoryComplaintEntity: ...
