from datetime import datetime
from typing import (
    Annotated,
    Type,
)

from api.mobile.depends import get_statistic_model
from api.pagination import LazyLoad
from api.schema import (
    PaginationIn,
    PaginationResponseSchema,
)

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from starlette import status

from apps.quiz.permissions.quiz import DevicePermissions
from apps.users.actions import (
    CompositeStatisticAction,
    ProfileActions,
    StatisticsActions,
)
from apps.users.models import Statistic
from apps.users.permissions.profile import ProfilePermissions
from config.containers import (
    Container,
    get_container,
)
from core.database.db import Base
from core.security.fingerprint_auth.device_validator import DeviceTokenValidate
from core.security.fingerprint_auth.mobile_auth import (
    http_device,
    MobileAuthorizationCredentials,
)
from services.firebase import check_firebase_apikey
from services.mapper import (
    convert_to_ladder_statistic,
    convert_to_statistic_retrieve_mobile,
    dataclass_to_schema,
)

from ..utils import get_offset
from .schema import (
    ApiKeySchema,
    LadderStatisticRetrieveSchema as LdrSchema,
    ProfileSchema,
    StatisticsRetrieveSchema,
    StatisticsUpdateSchema,
    UpdateProfileSchema,
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

    action: ProfileActions = container.resolve(ProfileActions)
    profile = await action.create(cred.token)
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
    profile = await actions.get_profile(id=pk)
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
    profile = await actions.patch_profile(pk, name=profile.name)
    return dataclass_to_schema(ProfileSchema, profile)


@router.post("/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def set_user_statistic(
    pk: int,
    stat: StatisticsUpdateSchema,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    container: Container = Depends(get_container),
) -> StatisticsRetrieveSchema:
    """
    Записать статистику за игру у пользователя.\n\n
    pk: pk - id профиля пользователя\n\n
    score: набранные за игру очки\n\n
    rights: количество верных ответов за игру\n\n
    wrongs: количество неверных ответов за игру
    """
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    composite: CompositeStatisticAction = container.resolve(
        CompositeStatisticAction
    )
    await composite.patch(
        profile_pk=pk,
        score=stat.score,
        rights=stat.rights,
        wrongs=stat.wrongs,
        perfect_round=stat.perfect_round,
    )

    action: StatisticsActions = container.resolve(StatisticsActions[Statistic])
    stat, title = await action.get_by_profile(pk)

    profile_action: ProfileActions = container.resolve(ProfileActions)
    await profile_action.patch_profile(pk=pk, last_visit=datetime.now())
    return convert_to_statistic_retrieve_mobile(stat, title)


@router.get("/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def get_user_statistic(
    pk: int,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    model: Type[Base] = Depends(get_statistic_model),
    container: Container = Depends(get_container),
) -> StatisticsRetrieveSchema:
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    actions: StatisticsActions = container.resolve(StatisticsActions[model])
    stat, title = await actions.get_by_profile(pk)
    return convert_to_statistic_retrieve_mobile(stat, title)


@router.get(
    path="/user_statistic/{pk}/ladder/",
    status_code=status.HTTP_200_OK,
    description="Топ игроков, текущий юзер в середине ладдера",
)
async def get_ladder_profile(
    pk: int,
    limit: Annotated[int, Query(ge=0, le=200)] = 60,
    cred: MobileAuthorizationCredentials = Depends(http_device),
    model: Type[Base] = Depends(get_statistic_model),
    container: Container = Depends(get_container),
) -> PaginationResponseSchema[LdrSchema]:
    permissions: ProfilePermissions = container.resolve(ProfilePermissions)
    await permissions.has_permission(pk, cred.token)

    action: StatisticsActions = container.resolve(StatisticsActions[model])
    # offset рассчитывается, чтобы профиль был в середине
    offset = await get_offset(action, pk, limit)
    pagination_in = PaginationIn(limit=limit, offset=offset)

    paginator = LazyLoad(
        pagination=pagination_in,
        action=action,
    )
    statistics_page = paginator.paginate(action.get_top_ladder)

    result = await statistics_page(offset, limit)
    result.items = [
        convert_to_ladder_statistic(item)  # type: ignore
        for item in result.items
    ]
    return result


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
    model: Type[Base] = Depends(get_statistic_model),
    container: Container = Depends(get_container),
) -> PaginationResponseSchema[LdrSchema]:
    permissions: DevicePermissions = container.resolve(DevicePermissions)
    await permissions.has_permission(cred.token)

    action: StatisticsActions = container.resolve(StatisticsActions[model])

    paginator = LazyLoad(
        pagination=pagination_in,
        action=action,
    )
    statistics_page = paginator.paginate(action.get_top_ladder)
    result = await statistics_page(
        offset=pagination_in.offset, limit=pagination_in.limit
    )

    result.items = [
        convert_to_ladder_statistic(item)  # type: ignore
        for item in result.items
    ]
    return result
