from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from sqlalchemy.engine.row import Row

from apps.quiz.models import (
    Answer,
    CategoryComplaint,
    Complaint,
    Question,
)


@dataclass
class IQuestionService(ABC):
    @abstractmethod
    async def get_random(self, limit: int) -> list[Question]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> Question: ...

    @abstractmethod
    async def get_by_id_with_complaints_count(
        self,
        pk: int,
    ) -> Row[Question, int]: ...

    @abstractmethod
    async def get_list_with_complaints_count(
        self,
        offset: int,
        limit: int = 100,
        search: str | None = None,
    ) -> list[Row[Question, int]]: ...

    @abstractmethod
    async def get_count(self, search: str | None = None) -> int: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...

    @abstractmethod
    async def create(self, text: str, published: bool) -> Question: ...

    @abstractmethod
    async def create_from_json(
        self,
        question_text: str,
        question_published: bool,
        answers: list[dict[str, str | bool]],
    ) -> tuple[Question, list[Answer]]: ...

    @abstractmethod
    async def update_from_json(
        self,
        question_id: int,
        question_text: str,
        question_published: bool,
        answers: list[dict[str, str | bool | int]],
    ) -> tuple[Question, list[Answer]]: ...

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
    ) -> Answer: ...

    @abstractmethod
    async def update(
        self,
        pk: int,
        **fields,
    ) -> Answer: ...

    @abstractmethod
    async def exists_by_id(self, pk: int) -> bool: ...


@dataclass
class IComplaintService(ABC):
    @abstractmethod
    async def create(
        self,
        text: str,
        question_id: int,
        profile_id: int,
        category_id: int,
    ) -> Complaint: ...

    @abstractmethod
    async def get_by_id(self, question_id: int) -> Complaint: ...

    @abstractmethod
    async def get_list(
        self,
        offset: int,
        limit: int = 100,
    ) -> list[Complaint]: ...

    @abstractmethod
    async def get_count(self) -> int: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...


@dataclass
class ICategoryComplaintService(ABC):
    @abstractmethod
    async def list(self) -> list[CategoryComplaint]: ...

    @abstractmethod
    async def get_by_id(self, pk: int) -> CategoryComplaint: ...
