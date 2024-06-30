from dataclasses import dataclass
from core.services.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class InvalidProfile(BaseHTTPException):
    code: int = 401,
    detail: str = "Предоставлены некорректные данные авторизации"


@dataclass(eq=False)
class DoesNotExistsProfile(BaseHTTPException):
    code: int = 400
    detail: str = "Такой профиль не найден"


@dataclass(eq=False)
class AlreadyExistsProfile(BaseHTTPException):
    code: int = 400
    detail: str = "Для этого устройства уже создан профиль"


@dataclass(eq=False)
class ProfileDoesNotMatchTheDevice(BaseHTTPException):
    code: int = 403
    detail: str = "Этот профиль не соответствует устройству"
