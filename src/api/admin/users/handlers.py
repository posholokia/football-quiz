from api.pagination import PagePaginator
from api.schema import (
    PagePaginationIn,
    PagePaginationResponseSchema,
)
from punq import Container

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.users.actions import ProfileActions
from apps.users.models import UserEntity
from apps.users.permissions.admin import IsAdminUser
from config.containers import get_container
from services.mapper import Mapper

from ..depends import get_user_from_token
from .schema import ProfileAdminRetrieveSchema


router = APIRouter()


@router.get(
    "/admin/profiles/",
    status_code=status.HTTP_200_OK,
    description="Получить список вопросов\n\nПагинация:\n\n"
    ":: page - номер запрошенной страницы\n\n"
    ":: limit - кол-во записей на странице\n\n"
    ":: pages - всего страницы для заданного limit",
)
async def get_list_profiles(
    search: str | None = None,
    pagination_in: PagePaginationIn = Depends(),
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> PagePaginationResponseSchema[ProfileAdminRetrieveSchema]:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: ProfileActions = container.resolve(ProfileActions)
    paginator: PagePaginator = container.resolve(
        service_key=PagePaginator,
        pagination=pagination_in,
        schema=ProfileAdminRetrieveSchema,
        action=action,
    )
    res = await paginator.paginate(action.get_list)

    return await res(pagination_in.page, pagination_in.limit, search)


@router.post(
    "/admin/profiles/reset_name/{profile_id}/",
    status_code=status.HTTP_200_OK,
    description="Сброс имени пользователя",
)
async def reset_profile_name(
    profile_id: int,
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> ProfileAdminRetrieveSchema:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: ProfileActions = container.resolve(ProfileActions)

    profile = await action.reset_name(profile_id)

    return await Mapper.dataclass_to_schema(
        ProfileAdminRetrieveSchema,
        profile,
    )
