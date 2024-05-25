from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status

from mobile.users.schema import ProfileSchema

from core.database.db import get_session
from core.database.crud import ProfileCRUD
from core.security.mobile_auth import MobileAuthorizationCredentials
from core.security.utils import check_device_permissions, check_device_token
from ..depends import get_auth_credentials

router = APIRouter()
http_bearer = HTTPBearer()


@router.post("/create_profile/", status_code=status.HTTP_201_CREATED)
async def create_profile(
    session: AsyncSession = Depends(get_session),
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Создать профиль игрока"""
    if cred.type == "device":
        await check_device_token(cred.token)
    crud = ProfileCRUD(session)
    profile = await crud.create(cred.token)
    return profile


@router.get("/get_profile/{pk}", status_code=status.HTTP_200_OK)
async def get_profile(
    pk: int,
    session: AsyncSession = Depends(get_session),
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    """Получить данные профиля по id"""
    await check_device_permissions(pk, cred, session)
    crud = ProfileCRUD(session)
    profile = await crud.get(pk)
    return profile


@router.patch("/change_name/{pk}")
async def change_name(
    pk: int,
    name: str,
    session: AsyncSession = Depends(get_session),
    cred: MobileAuthorizationCredentials = Depends(get_auth_credentials),
) -> ProfileSchema:
    await check_device_permissions(pk, cred, session)
    crud = ProfileCRUD(session)
    profile = await crud.patch(pk, name=name)
    return profile
