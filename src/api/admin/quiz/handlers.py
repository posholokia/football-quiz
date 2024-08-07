from api.admin.quiz.schema import (
    QuestionAdminRetrieveSchema,
    QuestionFullCreateSchema,
)
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

from apps.quiz.actions.questions import QuestionsActions
from apps.users.models import UserEntity
from apps.users.permissions.admin import IsAdminUser
from config.containers import get_container
from services.mapper import Mapper

from ..depends import get_user_from_token


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


@router.delete(
    "/admin/question/{question_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление вопроса",
)
async def delete_question(
    question_id: int,
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> None:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: QuestionsActions = container.resolve(QuestionsActions)
    await action.delete_question(question_id)
    return None


@router.post(
    "/admin/question/",
    status_code=status.HTTP_200_OK,
    description="Создание вопроса вместе с ответами",
)
async def create_question(
    question: QuestionFullCreateSchema,
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> QuestionAdminRetrieveSchema:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: QuestionsActions = container.resolve(QuestionsActions)
    q = await action.create_question_with_answers(question)
    return Mapper.dataclass_to_schema(QuestionAdminRetrieveSchema, q)
