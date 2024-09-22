from typing import Type

from api.mobile.depends import get_statistic_model

from fastapi import (
    APIRouter,
    Depends,
)
from starlette import status

from apps.users.actions import StatisticsActions
from config.containers import (
    Container,
    get_container,
)
from core.database.db import Base
from services.mapper import convert_to_statistic_retrieve_mobile as convert

from .schema import StatisticsRetrieveSchema


router = APIRouter()


@router.get("/web/user_statistic/{pk}/", status_code=status.HTTP_200_OK)
async def get_user_statistic(
    pk: int,
    model: Type[Base] = Depends(get_statistic_model),
    container: Container = Depends(get_container),
) -> StatisticsRetrieveSchema:
    actions: StatisticsActions = container.resolve(StatisticsActions[model])
    stat, title = await actions.get_by_profile(pk)
    return convert(stat, title)
