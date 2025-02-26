from api.pagination import PagePaginator
from api.schema import (
    PagePaginationIn,
    PagePaginationResponseSchema,
)

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.users.actions import ProfileActions
from config.containers import (
    Container,
    get_container,
)
from services.mapper import convert_to_profile_retrieve_admin as convert

from ..depends import is_admin_permission
from .schema import ProfileAdminRetrieveSchema as PrfSchema


router = APIRouter()


@router.get(
    "/admin/profiles/",
    status_code=status.HTTP_200_OK,
    description="Получить список игроков\n\nПагинация:\n\n"
    ":: page - номер запрошенной страницы\n\n"
    ":: limit - кол-во записей на странице\n\n"
    ":: pages - всего страницы для заданного limit",
)
async def get_list_profiles(
    search: str | None = None,
    pagination_in: PagePaginationIn = Depends(),
    _=Depends(is_admin_permission),
    container: Container = Depends(get_container),
) -> PagePaginationResponseSchema[PrfSchema]:
    action: ProfileActions = container.resolve(ProfileActions)
    paginator = PagePaginator(pagination=pagination_in, action=action)
    profile_page = paginator.paginate(action.get_list_admin)
    result = await profile_page(
        pagination_in.page, pagination_in.limit, search
    )
    result.items = [
        convert(profile, complaints) for profile, complaints in result.items
    ]
    return result


@router.post(
    "/admin/profiles/reset_name/{profile_id}/",
    status_code=status.HTTP_200_OK,
    description="Сброс имени пользователя",
)
async def reset_profile_name(
    profile_id: int,
    _=Depends(is_admin_permission),
    container: Container = Depends(get_container),
) -> PrfSchema:
    action: ProfileActions = container.resolve(ProfileActions)
    profile, complaints = await action.reset_name(profile_id)
    return convert(profile, complaints)
