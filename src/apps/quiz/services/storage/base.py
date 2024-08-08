from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from apps.quiz.models import (
    AnswerEntity,
    CategoryComplaintEntity,
    ComplaintEntity,
    QuestionAdminDTO,
    QuestionEntity,
)
from apps.users.models import ProfileEntity


@dataclass
class IQuestionService(ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> list[QuestionEntity]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> QuestionEntity: ...

    @abstractmethod
    async def get_by_id_with_complaints_count(
        self,
        pk: int,
    ) -> QuestionAdminDTO: ...

    @abstractmethod
    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int = 100,
        search: str | None = None,
    ) -> list[QuestionAdminDTO]: ...

    @abstractmethod
    async def get_count(self, search: str | None = None) -> int: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...

    @abstractmethod
    async def create(self, text: str, published: bool) -> QuestionEntity: ...

    @abstractmethod
    async def create_from_json(
        self,
        question_text: str,
        question_published: bool,
        answers: list[dict[str, str | bool]],
    ) -> QuestionAdminDTO: ...

    @abstractmethod
    async def update_from_json(
        self,
        question_id: int,
        question_text: str,
        question_published: bool,
        question_complaints: int,
        answers: list[dict[str, str | bool | int]],
    ) -> QuestionAdminDTO: ...

    @abstractmethod
    async def exists_by_id(self, pk: int) -> bool: ...


@dataclass
class IAnswerService(ABC):
    @abstractmethod
    async def create(
        self,
        text: str,
        right: bool,
        question_id: int,
    ) -> AnswerEntity: ...

    @abstractmethod
    async def update(
        self,
        pk: int,
        **fields,
    ) -> AnswerEntity: ...

    @abstractmethod
    async def exists_by_id(self, pk: int) -> bool: ...


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
    async def get_by_id(self, question_id: int) -> ComplaintEntity: ...

    @abstractmethod
    async def get_list(
        self,
        offset: int,
        limit: int = 100,
    ) -> list[ComplaintEntity]: ...

    @abstractmethod
    async def get_count(self) -> int: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...


@dataclass
class ICategoryComplaintService(ABC):
    @abstractmethod
    async def list(self) -> list[CategoryComplaintEntity]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> CategoryComplaintEntity: ...
