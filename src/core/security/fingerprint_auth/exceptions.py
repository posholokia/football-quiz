from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class UnauthorizedDevice(BaseHTTPException):
    code: int = 401
    detail: str = "Предоставлены некорректные данные авторизации"


@dataclass(eq=False)
class InvalidDeviceToken(BaseHTTPException):
    code: int = 401
    detail: str = "Невалидный токен устройства"


@dataclass(eq=False)
class NotUniqueDeviceToken(BaseHTTPException):
    code: int = 401
    detail: str = "Токен устройства не уникален"
