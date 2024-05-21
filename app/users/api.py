from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status

from app.users.schema import ProfileSchema

from core.database.db import get_session
from core.database.crud import ProfileCRUD

router = APIRouter()


@router.post("/create_profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    session: AsyncSession = Depends(get_session),
) -> ProfileSchema:
    """Создать профиль игрока"""
    crud = ProfileCRUD(session)
    profile = await crud.create()
    return profile


@router.get("/get_profile/{pk}", status_code=status.HTTP_200_OK)
async def get_profile(
    pk: int,
    session: AsyncSession = Depends(get_session),
) -> ProfileSchema:
    """Получить данные профиля по id"""
    crud = ProfileCRUD(session)
    profile = await crud.get(pk)
    return profile
