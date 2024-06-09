from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer
from starlette import status

from apps.quiz.schema import QuestionSchema
from core.actions import QuestionsActions
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import check_device_profile_exists

from .depends import get_auth_credentials


router = APIRouter()
http_bearer = HTTPBearer()


@router.get("/get_questions/", status_code=status.HTTP_200_OK)
async def get_questions(
    limit: int = 10,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> list[QuestionSchema]:
    """Получение выборки вопросов"""
    await check_device_profile_exists(cred)
    crud = await QuestionsActions.start_session()
    questions = await crud.get(limit)
    return questions
