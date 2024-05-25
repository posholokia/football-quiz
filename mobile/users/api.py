from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status

from mobile.users.schema import ProfileSchema, SetStatisticsSchema, GetStatisticsSchema

from core.database.db import get_session
from core.database.crud import ProfileCRUD, StatisticsCRUD
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import check_device_permissions, check_device_token
from ..depends import get_auth_credentials

router = APIRouter()
http_bearer = HTTPBearer()


@router.post("/create_profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
        session: AsyncSession = Depends(get_session),
        cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Создать профиль игрока"""
    if cred.type == "device":
        await check_device_token(cred.token)
    crud = ProfileCRUD(session)
    profile = await crud.create(cred.token)
    return profile


@router.get("/get_profile/{pk}", status_code=status.HTTP_200_OK)
async def get_profile(
        pk: int,
        session: AsyncSession = Depends(get_session),
        cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Получить данные профиля по id"""
    await check_device_permissions(pk, cred, session)
    crud = ProfileCRUD(session)
    profile = await crud.get(pk)
    return profile


@router.patch("/change_name/{pk}", status_code=status.HTTP_200_OK)
async def change_name(
        pk: int,
        name: str,
        session: AsyncSession = Depends(get_session),
        cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Смена имени пользователя"""
    await check_device_permissions(pk, cred, session)
    crud = ProfileCRUD(session)
    profile = await crud.patch(pk, name=name)
    return profile


@router.post("/user_statistic/{pk}/")
async def set_user_statistic(
        pk: int,
        stat: SetStatisticsSchema,
        session: AsyncSession = Depends(get_session),
        cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
):# -> GetStatisticsSchema:
    """
    Записать статистику за игру у пользователя.\n\n
    pk: pk - id профиля пользователя\n\n
    score: набранные за игру очки\n\n
    rights: количество верных ответов за игру\n\n
    wrongs: количество неверных ответов за игру
    """
    await check_device_permissions(pk, cred, session)
    crud = StatisticsCRUD(session)
    user_stat = await crud.patch(pk, stat)
    return 200
    # return user_stat


@router.get("/user_statistic/{pk}")
async def get_user_statistic(
        pk: int,
):
    return {
        "status": 200,
        "general_score": 17,
        "games": 2,
        "place": 20
    }
