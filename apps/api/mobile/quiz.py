from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

from starlette import status

from services.crud_service import QuestionsCRUD
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import check_device_profile_exists
from apps.quiz.schema import QuestionSchema
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
    crud = await QuestionsCRUD.start()
    async with crud.session.begin():
        questions = await crud.get(limit)
    return questions
