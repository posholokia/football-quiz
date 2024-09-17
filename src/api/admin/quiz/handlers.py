import json

from api.admin.quiz.schema import (
    ComplaintAdminRetrieveSchema,
    QuestionAdminRetrieveSchema,
    QuestionFullCreateSchema,
    QuestionFullUpdateSchema, QuestionWithRelationshipsSchema,
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

from apps.quiz.actions import ComplaintsActions
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
    question_dict = json.loads(question.json())
    q = await action.create_question_with_answers(question_dict)
    return Mapper.dataclass_to_schema(QuestionAdminRetrieveSchema, q)


@router.put(
    "/admin/question/{question_id}/",
    status_code=status.HTTP_200_OK,
    description="Удаление вопроса",
)
async def update_question(
    question: QuestionFullUpdateSchema,
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> QuestionAdminRetrieveSchema:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: QuestionsActions = container.resolve(QuestionsActions)
    question_dict = json.loads(question.json())
    q = await action.update_question_with_answers(question_dict)
    return Mapper.dataclass_to_schema(QuestionAdminRetrieveSchema, q)


@router.get(
    "/admin/question/{question_id}/",
    status_code=status.HTTP_200_OK,
    description="Получить вопрос по id.",
)
async def update_question(
    question_id: int,
    # user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> QuestionWithRelationshipsSchema:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    # await permission.has_permission(user)

    action: QuestionsActions = container.resolve(QuestionsActions)
    question = await action.get_with_complaints(question_id)
    return Mapper.dataclass_to_schema(QuestionWithRelationshipsSchema, question)


@router.get(
    "/admin/complaint/",
    status_code=status.HTTP_200_OK,
    description="Получить список жалоб\n\nПагинация:\n\n"
    ":: page - номер запрошенной страницы\n\n"
    ":: limit - кол-во записей на странице\n\n"
    ":: pages - всего страницы для заданного limit",
)
async def get_list_complaints(
    pagination_in: PagePaginationIn = Depends(),
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> PagePaginationResponseSchema[ComplaintAdminRetrieveSchema]:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: ComplaintsActions = container.resolve(ComplaintsActions)
    paginator: PagePaginator = container.resolve(
        service_key=PagePaginator,
        pagination=pagination_in,
        schema=ComplaintAdminRetrieveSchema,
        action=action,
    )
    res = await paginator.paginate(action.get_list)

    return await res(pagination_in.page, pagination_in.limit)


@router.delete(
    "/admin/complaint/{complaint_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление жалобы",
)
async def delete_complaint(
    complaint_id: int,
    user: UserEntity = Depends(get_user_from_token),
    container: Container = Depends(get_container),
) -> None:
    permission: IsAdminUser = container.resolve(IsAdminUser)
    await permission.has_permission(user)

    action: ComplaintsActions = container.resolve(ComplaintsActions)
    await action.delete_complaint(complaint_id)
    return None
