from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from starlette import status

from core.api.mobile.depends import get_auth_credentials
from core.apps.quiz.actions import QuestionsActions
from core.apps.quiz.dto import QuestionDTO
from core.apps.quiz.permissions.quiz import DevicePermissions
from core.apps.quiz.schema import QuestionSchema
from core.services.security.mobile_auth import MobileAuthorizationCredentials
from core.config.containers import get_container

router = APIRouter()


@router.get("/get_questions/", status_code=status.HTTP_200_OK)
async def get_questions(
    limit: Annotated[int, Query(ge=1, le=30)] = 10,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> list[QuestionSchema]:
    """Получение выборки вопросов"""
    container = get_container()
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    actions: QuestionsActions = container.resolve(QuestionsActions)
    questions: list[QuestionDTO] = await actions.get_random(limit)
    return [QuestionSchema.from_dto(q) for q in questions]


# @router.post("/complain/", status_code=status.HTTP_200_OK)
# async def create_complaint(
#     complaint: CreateComplaintSchema,
#     cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
# ) -> RetrieveComplaintSchema:
#     """Оставить жалобу"""
#     await check_device_profile_exists(cred)
#     crud = await ComplaintsActions.start_session()
#     questions = await crud.create(
#         text=complaint.text,
#         question_id=complaint.question,
#         token=cred.token,
#     )
#     return questions

