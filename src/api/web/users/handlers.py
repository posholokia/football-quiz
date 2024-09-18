from typing import (
    Type,
)

from api.mobile.depends import get_statistic_model

from punq import Container

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.users.actions import (
    StatisticsActions,
)

from config.containers import get_container
from core.database.db import Base

from services.mapper import Mapper

from .schema import (
    StatisticsRetrieveSchema,
)


router = APIRouter()


@router.get("/web/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def get_user_statistic(
    pk: int,
    model: Type[Base] = Depends(get_statistic_model),
    container: Container = Depends(get_container),
) -> StatisticsRetrieveSchema:

    actions: StatisticsActions = container.resolve(
        StatisticsActions, model=model
    )
    stat = await actions.get_by_profile(pk)
    return Mapper.dataclass_to_schema(StatisticsRetrieveSchema, stat)