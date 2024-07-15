from dataclasses import dataclass

from core.services.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class InvalidProfile(BaseHTTPException):
    code: int = 401
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


@dataclass(eq=False)
class InvalidProfileName(BaseHTTPException):
    code: int = 400
    detail: str = "Некорректное имя пользователя"


@dataclass(eq=False)
class ProfileNameIsProfanity(BaseHTTPException):
    code: int = 422
    detail: str = "Имя пользователя содержит нецензурную лексику"


@dataclass(eq=False)
class ProfanityServiceNotAvailable(BaseHTTPException):
    code: int = 500
    detail: str = "Сервис проверки нецензурной лексики недоступен"
