from typing import Annotated

from punq import Container

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from starlette import status

from apps.quiz.actions import (
    CategoryComplaintsActions,
    ComplaintsActions,
    QuestionsActions,
)
from apps.quiz.dto import QuestionDTO
from apps.quiz.permissions.quiz import DevicePermissions
from apps.users.permissions.profile import ProfilePermissions
from config.containers import get_container
from core.security.fingerprint_auth.mobile_auth import (
    http_device,
    MobileAuthorizationCredentials,
)
from services.mapper import Mapper

from .schema import (
    CreateComplaintSchema,
    QuestionSchema,
    RetrieveCategorySchema,
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
    return [Mapper.dataclass_to_schema(QuestionSchema, q) for q in questions]


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
    return [
        Mapper.dataclass_to_schema(RetrieveCategorySchema, cat)
        for cat in categories_list
    ]
