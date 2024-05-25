from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.crud.questions import QuestionsCRUD
from core.database.db import get_session
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import get_device_exists_profile
from .schema import QuestionSchema
from ..depends import get_auth_credentials

router = APIRouter()
http_bearer = HTTPBearer()


@router.get("/get_questions/")
async def get_questions(
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> list[QuestionSchema]:
    """Получение выборки вопросов"""
    if cred.type == "device":
        await get_device_exists_profile(cred.token, session)
    crud = QuestionsCRUD(session)
    questions = await crud.get(limit)
    return questions
