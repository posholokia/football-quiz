from typing import Annotated

from punq import Container

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from starlette import status

from core.apps.quiz.actions import QuestionsActions
from core.apps.quiz.actions.actions import (
    CategoryComplaintsActions,
    ComplaintsActions,
)
from core.apps.quiz.dto import QuestionDTO
from core.apps.quiz.permissions.quiz import DevicePermissions
from core.apps.quiz.schema import (
    CreateComplaintSchema,
    QuestionSchema,
    RetrieveCategorySchema,
)
from core.apps.users.permissions.profile import ProfilePermissions
from core.config.containers import get_container
from core.services.security.mobile_auth import (
    http_device,
    MobileAuthorizationCredentials,
)


router = APIRouter()


@router.get("/get_questions/", status_code=status.HTTP_200_OK)
async def get_questions(
    limit: Annotated[int, Query(ge=1, le=30)] = 10,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> list[QuestionSchema]:
    """Получение выборки вопросов"""
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    actions: QuestionsActions = container.resolve(QuestionsActions)
    questions: list[QuestionDTO] = await actions.get_random(limit)
    return [QuestionSchema.from_dto(q) for q in questions]


@router.post("/complain/", status_code=status.HTTP_204_NO_CONTENT)
async def create_complaint(
    complaint: CreateComplaintSchema,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> None:
    """Оставить жалобу"""
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(complaint.profile, cred.token)

    action: ComplaintsActions = container.resolve(ComplaintsActions)
    await action.create(
        text=complaint.text,
        question_id=complaint.question,
        profile_id=complaint.profile,
        category_id=complaint.category,
    )
    return None


@router.get("/complain/category/", status_code=status.HTTP_200_OK)
async def category_list(
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> list[RetrieveCategorySchema]:
    """Список категорий"""
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    action: CategoryComplaintsActions = container.resolve(
        CategoryComplaintsActions
    )
    categories_list = await action.list()
    return [RetrieveCategorySchema.from_dto(cat) for cat in categories_list]
