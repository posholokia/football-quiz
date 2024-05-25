from typing import Optional

from fastapi import HTTPException
from starlette import status

from fastapi import Depends
from fastapi.security import HTTPBearer

from core.security.mobile_auth import (
    HTTPDevice,
    MobileAuthorizationCredentials,
)

http_bearer_no_error = HTTPBearer(auto_error=False)
http_device = HTTPDevice()


async def get_auth_credentials(
    device: Optional[MobileAuthorizationCredentials] = Depends(http_device),
) -> MobileAuthorizationCredentials:
    """
    Получение токена приложения или токен аутентификации.
    Для аутентификации добавить в зависимость получение
    токена пользователя.
    """
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Запросы допустимы только из приложения",
        )
    else:
        return device
