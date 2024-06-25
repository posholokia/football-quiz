from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.api.actions.quiz import QuestionsActions
from apps.quiz.schema import (
    CreateComplaintSchema,
    QuestionSchema,
    RetrieveComplaintSchema,
)
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import check_device_profile_exists

from ..actions.quiz import ComplaintsActions
from .depends import get_auth_credentials


router = APIRouter()


@router.get("/get_questions/", status_code=status.HTTP_200_OK)
async def get_questions(
    limit: int = 10,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> list[QuestionSchema]:
    """Получение выборки вопросов"""
    await check_device_profile_exists(cred)
    crud = await QuestionsActions.start_session()
    questions = await crud.get_random(limit)
    return questions


@router.post("/complain/", status_code=status.HTTP_200_OK)
async def create_complaint(
    complaint: CreateComplaintSchema,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> RetrieveComplaintSchema:
    """Оставить жалобу"""
    await check_device_profile_exists(cred)
    crud = await ComplaintsActions.start_session()
    questions = await crud.create(
        text=complaint.text,
        question_id=complaint.question,
        token=cred.token,
    )
    return questions
