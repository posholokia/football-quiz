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

from .schema import FeedbackLeaveSchema


router = APIRouter()


@router.post(
    "/web/feedback/",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Оставить обратную связь.",
)
async def leave_feedback(
    feedback: FeedbackLeaveSchema,
    container: Container = Depends(get_container),
) -> None:
    action: FeedbackAction = container.resolve(FeedbackAction)
    await action.leave_feedback(
        name=feedback.name,
        email=feedback.email,
        text=feedback.text,
    )
