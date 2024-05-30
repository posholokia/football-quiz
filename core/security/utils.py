import string

from fastapi import HTTPException
from starlette import status

from core.security.mobile_auth import MobileAuthorizationCredentials

from services.crud_service import ProfileCRUD


async def check_device_token(token: str) -> None:
    allow_symbols = f"{string.ascii_lowercase}{string.digits}"
    if (len(token) != 32) or (
        not all(char in allow_symbols for char in token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный тип токена",
        )


async def check_device_profile_exists(
    cred: MobileAuthorizationCredentials,
) -> None:
    if cred.type == "device":
        await check_device_token(cred.token)
        crud = await ProfileCRUD.start()
        async with crud.session.begin():
            try:
                await crud.get_device_profile(cred.token)
            except TypeError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Некорректный токен устройства",
                )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )


async def check_device_permissions(
    pk: int,
    cred: MobileAuthorizationCredentials,
) -> None:
    if cred.type == "device":
        await check_device_token(cred.token)
        crud = await ProfileCRUD.start()
        async with crud.session.begin():
            profile = await crud.get(pk)

        if profile.device_uuid == cred.token:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
    )