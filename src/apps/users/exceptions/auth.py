from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class InvalidAuthCredentials(BaseHTTPException):
    code: int = 401
    detail: str = "Предоставлены неверные данные авторизации"


@dataclass(eq=False)
class InvalidToken(BaseHTTPException):
    code: int = 401
    detail: str = "Некорректный jwt токен"


@dataclass(eq=False)
class UserDoesNotExists(BaseHTTPException):
    code: int = 401
    detail: str = "Такой пользователь не найден"


@dataclass(eq=False)
class UserIsNotAdminError(BaseHTTPException):
    code: int = 403
    detail: str = "У пользователя недостаточно прав для выполнения действия"
