from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class InvalidAuthCredentials(BaseHTTPException):
    code: int = 401
    detail: str = "Предоставлены неверные данные авторизации"
