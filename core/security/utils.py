from sqlalchemy import select
import string
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from starlette import status

from mobile.users.models import Profile
from core.security.mobile_auth import MobileAuthorizationCredentials


async def check_device_token(token: str) -> None:
    allow_symbols = f"{string.ascii_lowercase}{string.digits}"
    if (len(token) != 32) or (
        not all(char in allow_symbols for char in token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный тип токена",
        )


async def get_device_exists_profile(
    token: str,
    session: AsyncSession,
) -> int:
    async with session.begin():
        stmt = select(Profile.id).where(Profile.device_uuid == token)
        result = await session.execute(stmt)
        profile_id = result.fetchone()

        if not profile_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный токен устройства",
            )

        return profile_id[0]


async def check_device_permissions(
    pk: int,
    cred: MobileAuthorizationCredentials,
    session: AsyncSession,
) -> None:
    if cred.type == "device":
        await check_device_token(cred.token)
        profile_id = await get_device_exists_profile(cred.token, session)

        if pk == profile_id:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
    )
