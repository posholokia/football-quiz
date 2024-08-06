from api.admin.depends import get_user_from_token
from api.admin.quiz.schema import QuestionAdminRetrieveSchema
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
from fastapi.security import HTTPBearer
from starlette import status

from apps.quiz.actions import QuestionsActions
from apps.users.models import UserEntity
from apps.users.permissions.admin import IsAdminUser
from config.containers import get_container


router = APIRouter()
http_bearer = HTTPBearer()


@router.get(
    "/admin/question/",
    status_code=status.HTTP_200_OK,
    description="Получить список вопросов\n\nПагинация:\n\n"
    ":: page - номер запрошенной страницы\n\n"
    ":: limit - кол-во записей на странице\n\n"
    ":: pages - всего страницы для заданного limit",
)
async def get_list_question(
    search: str | None = None,
    pagination_in: PagePaginationIn = Depends(),
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> PagePaginationResponseSchema[QuestionAdminRetrieveSchema]:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: QuestionsActions = container.resolve(QuestionsActions)
    paginator: PagePaginator = container.resolve(
        service_key=PagePaginator,
        pagination=pagination_in,
        schema=QuestionAdminRetrieveSchema,
        action=action,
    )
    res = await paginator.paginate(action.get_list)

    return await res(pagination_in.page, pagination_in.limit, search)