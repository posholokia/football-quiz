from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer
from starlette import status

from apps.users.schema import (
    ApiKeySchema,
    GetStatisticsSchema,
    ProfileSchema,
    SetStatisticsSchema,
    UpdateProfileSchema,
)
from core.actions import (
    ProfileActions,
    StatisticsActions,
)
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import (
    check_device_permissions,
    check_device_token,
)
from services.firebase import check_firebase_apikey

from .depends import get_auth_credentials


router = APIRouter()


@router.post("/create_profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    firebase_key: ApiKeySchema,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Создать профиль игрока"""
    if cred.type == "device":
        await check_device_token(cred.token)
    await check_firebase_apikey(firebase_key.api_key)

    crud = await ProfileActions.start_session()
    profile = await crud.create(cred.token)
    return profile


@router.get("/get_profile/{pk}/", status_code=status.HTTP_200_OK)
async def get_profile(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Получить данные профиля по id"""
    await check_device_permissions(pk, cred)
    crud = await ProfileActions.start_session()
    profile = await crud.get(pk)
    return profile


@router.patch("/change_profile/{pk}/", status_code=status.HTTP_200_OK)
async def change_profile(
    pk: int,
    profile: UpdateProfileSchema,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Смена имени пользователя"""
    await check_device_permissions(pk, cred)
    crud = await ProfileActions.start_session()
    profile = await crud.patch(
        pk,
        name=profile.name,
    )
    return profile


@router.post("/user_statistic/{pk}/")
async def set_user_statistic(
    pk: int,
    stat: SetStatisticsSchema,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> GetStatisticsSchema:
    """
    Записать статистику за игру у пользователя.\n\n
    pk: pk - id профиля пользователя\n\n
    score: набранные за игру очки\n\n
    rights: количество верных ответов за игру\n\n
    wrongs: количество неверных ответов за игру
    """
    await check_device_permissions(pk, cred)
    crud = await StatisticsActions.start_session()
    user_stat = await crud.patch(pk, stat)
    return user_stat


@router.get("/user_statistic/{pk}/")
async def get_user_statistic(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> GetStatisticsSchema:
    await check_device_permissions(pk, cred)
    crud = await StatisticsActions.start_session()
    stat = await crud.get_statistic(pk)
    return stat
