import math
from typing import Annotated

from punq import Container

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from starlette import status

from core.api.mapper import dataclass_to_schema
from core.api.pagination import LimitOffsetPaginator
from core.api.schema import PaginationIn
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
    PaginationResponseSchema,
    ProfileSchema,
    SetStatisticsSchema,
    UpdateProfileSchema,
)
from core.config.containers import get_container
from core.services.firebase import check_firebase_apikey
from core.services.security.device_validator import DeviceTokenValidate
from core.services.security.mobile_auth import (
    http_device,
    MobileAuthorizationCredentials,
)


router = APIRouter()


@router.post("/create_profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    firebase: ApiKeySchema,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> ProfileSchema:
    """Создать профиль игрока"""
    await check_firebase_apikey(firebase.api_key)

    device: DeviceTokenValidate = container.resolve(DeviceTokenValidate)
    await device.validate(cred)

    actions: ProfileActions = container.resolve(ProfileActions)
    profile: ProfileDTO = await actions.create(cred.token)
    return dataclass_to_schema(ProfileSchema, profile)


@router.get("/get_profile/{pk}/", status_code=status.HTTP_200_OK)
async def get_profile(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> ProfileSchema:
    """Получить данные профиля по id"""
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: ProfileActions = container.resolve(ProfileActions)
    profile: ProfileDTO = await actions.get_by_id(pk)
    return dataclass_to_schema(ProfileSchema, profile)


@router.patch("/change_profile/{pk}/", status_code=status.HTTP_200_OK)
async def change_profile(
    pk: int,
    profile: UpdateProfileSchema,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> ProfileSchema:
    """Смена имени пользователя"""
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: ProfileActions = container.resolve(ProfileActions)
    profile: ProfileDTO = await actions.patch_profile(pk, profile.name)
    return dataclass_to_schema(ProfileSchema, profile)


@router.post("/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def set_user_statistic(
    pk: int,
    stat: SetStatisticsSchema,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> GetStatisticsSchema:
    """
    Записать статистику за игру у пользователя.\n\n
    pk: pk - id профиля пользователя\n\n
    score: набранные за игру очки\n\n
    rights: количество верных ответов за игру\n\n
    wrongs: количество неверных ответов за игру
    """
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: StatisticsActions = container.resolve(StatisticsActions)
    stat = await actions.patch(pk, stat)
    return dataclass_to_schema(GetStatisticsSchema, stat)


@router.get("/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def get_user_statistic(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> GetStatisticsSchema:
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: StatisticsActions = container.resolve(StatisticsActions)
    stat = await actions.get_by_id(pk)
    return dataclass_to_schema(GetStatisticsSchema, stat)


@router.get(
    path="/user_statistic/{pk}/ladder/",
    status_code=status.HTTP_200_OK,
    description="Топ игроков, текущий юзер в середине ладдера",
)
async def get_ladder_profile(
    pk: int,
    limit: Annotated[int, Query(ge=0, le=200)] = 60,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> PaginationResponseSchema[GetStatisticsSchema]:
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    action: StatisticsActions = container.resolve(StatisticsActions)
    # offset рассчитывается, чтобы профиль был в середине
    user_rank = await action.get_user_rank(pk)
    offset = (
        0
        if math.ceil(limit / 2) > user_rank
        else user_rank - math.ceil(limit / 2)
    )
    pagination_in = PaginationIn(limit=limit, offset=offset)

    paginator: LimitOffsetPaginator = container.resolve(
        service_key=LimitOffsetPaginator,
        pagination=pagination_in,
        schema=GetStatisticsSchema,
    )

    res = await paginator.paginate(action.get_top_ladder)
    return await res(pagination_in.offset, pagination_in.limit)


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
    pagination_in: PaginationIn = Depends(),
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> PaginationResponseSchema[GetStatisticsSchema]:
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    action: StatisticsActions = container.resolve(StatisticsActions)
    paginator: LimitOffsetPaginator = container.resolve(
        service_key=LimitOffsetPaginator,
        pagination=pagination_in,
        schema=GetStatisticsSchema,
    )

    res = await paginator.paginate(action.get_top_ladder)

    return await res(pagination_in.offset, pagination_in.limit)
