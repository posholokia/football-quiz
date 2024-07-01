from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from core.api.mobile.depends import get_auth_credentials
from core.apps.users.actions import (
    ProfileActions,
    StatisticsActions,
)
from core.apps.users.dto import ProfileDTO
from core.apps.users.permissions.profile import ProfilePermissions
from core.apps.users.schema import (
    ApiKeySchema,
    GetStatisticsSchema,
    ProfileSchema,
    SetStatisticsSchema,
    UpdateProfileSchema,
)
from core.config.containers import get_container
from core.services.firebase import check_firebase_apikey
from core.services.security.device_validator import DeviceTokenValidate
from core.services.security.mobile_auth import MobileAuthorizationCredentials


router = APIRouter()


@router.post("/create_profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    firebase: ApiKeySchema,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Создать профиль игрока"""
    await check_firebase_apikey(firebase.api_key)

    container = get_container()
    device: DeviceTokenValidate = container.resolve(DeviceTokenValidate)
    await device.validate(cred)

    actions: ProfileActions = container.resolve(ProfileActions)
    profile: ProfileDTO = await actions.create(cred.token)
    return ProfileSchema.from_dto(profile)


@router.get("/get_profile/{pk}/", status_code=status.HTTP_200_OK)
async def get_profile(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Получить данные профиля по id"""
    container = get_container()
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: ProfileActions = container.resolve(ProfileActions)
    profile: ProfileDTO = await actions.get_by_id(pk)
    return ProfileSchema.from_dto(profile)


@router.patch("/change_profile/{pk}/", status_code=status.HTTP_200_OK)
async def change_profile(
    pk: int,
    profile: UpdateProfileSchema,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Смена имени пользователя"""
    container = get_container()
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: ProfileActions = container.resolve(ProfileActions)
    profile: ProfileDTO = await actions.patch_profile(pk, profile.name)
    return ProfileSchema.from_dto(profile)


@router.post("/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
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
    container = get_container()
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: StatisticsActions = container.resolve(StatisticsActions)
    stat = await actions.patch(pk, stat)
    return GetStatisticsSchema.from_dto(stat)


@router.get("/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def get_user_statistic(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> GetStatisticsSchema:
    container = get_container()
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: StatisticsActions = container.resolve(StatisticsActions)
    stat = await actions.get_by_id(pk)
    return GetStatisticsSchema.from_dto(stat)
