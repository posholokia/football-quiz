from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class StatisticDoseNotExists(BaseHTTPException):
    code: int = 400
    detail: str = "Статистика не найдена"
