import http
from dataclasses import dataclass
from starlette.exceptions import HTTPException


@dataclass(eq=False)
class BaseHTTPException(Exception):
    code: int = 500
    detail: str = "Непредвиденная ошибка приложения"
