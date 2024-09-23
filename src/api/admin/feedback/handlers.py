from api.admin.depends import is_admin_permission
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

from apps.feedback.actions.feedback import FeedbackAction
from config.containers import (
    Container,
    get_container,
)
from services.mapper import dataclass_to_schema

from .schema import FeedbackRetrieveSchema


router = APIRouter()


@router.get(
    "/admin/feedback/",
    status_code=status.HTTP_200_OK,
    description="Просмотреть полученную обратную связь.",
)
async def review_feedback(
    pagination_in: PagePaginationIn = Depends(),
    _=Depends(is_admin_permission),
    container: Container = Depends(get_container),
) -> PagePaginationResponseSchema[FeedbackRetrieveSchema]:
    action: FeedbackAction = container.resolve(FeedbackAction)
    paginator = PagePaginator(pagination=pagination_in, action=action)
    feedback_page = paginator.paginate(action.review_feedback)
    result = await feedback_page(pagination_in.page, pagination_in.limit)
    result.items = [
        dataclass_to_schema(FeedbackRetrieveSchema, f) for f in result.items
    ]
    return result
