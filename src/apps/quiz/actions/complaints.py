from dataclasses import dataclass

from apps.quiz.exceptions import (
    CategoryComplaintDoesNotExists,
    QuestionDoesNotExists,
)
from apps.quiz.models import (
    CategoryComplaintEntity,
    ComplaintEntity,
)
from apps.quiz.services.storage.base import (
    ICategoryComplaintService,
    IComplaintService,
    IQuestionService,
)
from apps.users.exceptions.profile import DoesNotExistsProfile
from apps.users.services.storage.base import IProfileService


@dataclass
class ComplaintsActions:
    complaint_repository: IComplaintService
    profile_repository: IProfileService
    question_repository: IQuestionService
    category_repository: ICategoryComplaintService

    async def create(
        self,
        text: str,
        question_id: int,
        category_id: int,
        profile_id: int,
    ) -> ComplaintEntity:
        """
        Создать жалобу.

        :param text:        Текст жалобы.
        :param question_id: ID вопроса, на который жалоба.
        :param category_id: ID категории жалобы.
        :param profile_id:  ID профиля игрока, который оставил жалобу.
        :return:            Жалоба.
        """
        if not await self.profile_repository.exists(id=profile_id):
            raise DoesNotExistsProfile(
                detail=f"Профиль с id={profile_id} не найден."
            )
        elif not await self.question_repository.exists(id=question_id):
            raise QuestionDoesNotExists(
                detail=f"Вопрос с id={question_id} не найден."
            )
        elif not await self.category_repository.exists(id=category_id):
            raise CategoryComplaintDoesNotExists(
                detail=f"Категория с id={category_id} не найдена."
            )

        complaint = await self.complaint_repository.create(
            text=text,
            question_id=question_id,
            profile_id=profile_id,
            category_id=category_id,
        )
        return complaint

    async def get_list(
        self,
        page: int,
        limit: int,
    ) -> list[ComplaintEntity]:
        """
        Получить список жалоб.

        :param page:    Номер страницы с жалобами.
        :param limit:   Размер страницы.
        :return:        Список жалоб.
        """
        offset = (page - 1) * limit
        return await self.complaint_repository.get_list(offset, limit)

    async def get_count(self) -> int:
        """
        Получить кол-во жалоб.

        :return: Число жалоб.
        """
        return await self.complaint_repository.get_count()

    async def delete_complaint(self, pk: int) -> None:
        """
        Удалить жалобу.

        :param pk:  ID жалобы.
        :return:    None.
        """
        await self.complaint_repository.delete(pk)


@dataclass
class CategoryComplaintsActions:
    category_repository: ICategoryComplaintService

    async def list(self) -> list[CategoryComplaintEntity]:
        """
        Получить список категорий жалоб.

        :return: Список жалоб.
        """
        return await self.category_repository.list()
