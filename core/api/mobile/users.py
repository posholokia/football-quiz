import math
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from starlette import status

from core.api.mobile.depends import get_auth_credentials
from core.api.schema import PaginationOut
from core.apps.quiz.permissions.quiz import DevicePermissions
from core.apps.users.actions import (
    ProfileActions,
    StatisticsActions,
)
from core.apps.users.dto import ProfileDTO
from core.apps.users.permissions.profile import ProfilePermissions
from core.apps.users.schema import (
    ApiKeySchema,
    GetStatisticsSchema,
    PaginationStatisticSchema,
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


@router.get(
    path="/user_statistic/{pk}/ladder/",
    status_code=status.HTTP_200_OK,
    description="Топ игроков, текущий юзер в середине ладдера",
)
async def get_ladder_profile(
    pk: int,
    limit: Annotated[int, Query(ge=0, le=200)] = 60,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> PaginationStatisticSchema:
    container = get_container()
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    action: StatisticsActions = container.resolve(StatisticsActions)
    total = await action.get_count_statistic()

    # offset рассчитывается, чтобы профиль был в середине
    user_rank = await action.get_user_rank(pk)
    offset = (
        0
        if math.ceil(limit / 2) > user_rank
        else user_rank - math.ceil(limit / 2)
    )

    statistics = await action.get_top_ladder(offset=offset, limit=limit)
    return PaginationStatisticSchema(
        items=[GetStatisticsSchema.from_dto(obj) for obj in statistics],
        paginator=PaginationOut(
            offset=offset,
            limit=limit,
            total=total,
        ),
    )


@router.get(
    path="/ladder/top/",
    status_code=status.HTTP_200_OK,
    description="Топ игроков\n\nПагинация:\n\n"
    "::  limit: Сколько записей получить\n\n"
    "::  offset: начиная с какой записи получить данные. "
    "offset начинается с 0 и не включается в выборку.\n\n"
    '::  "/?limit=10&offset=0" покажет записи с 1 до 10 включительно\n\n'
    '::  "/?limit=10&offset=10" покажет записи с 11 до 20 включительно.\n\n'
    "В ответе paginator:\n\n"
    "::  offset: с какой записи запрошены объекты\n\n"
    "::  limit: сколько запрошено объектов\n\n"
    "::  total: всего объектов",
)
async def get_ladder(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=200)] = 30,
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> PaginationStatisticSchema:
    container = get_container()
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    action: StatisticsActions = container.resolve(StatisticsActions)
    statistics = await action.get_top_ladder(offset, limit)
    total = await action.get_count_statistic()
    return PaginationStatisticSchema(
        items=[GetStatisticsSchema.from_dto(obj) for obj in statistics],
        paginator=PaginationOut(
            offset=offset,
            limit=limit,
            total=total,
        ),
    )
