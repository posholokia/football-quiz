from dataclasses import dataclass


@dataclass(eq=False)
class BaseHTTPException(Exception):
    code: int = 500
    detail: str = "Непредвиденная ошибка приложения"
