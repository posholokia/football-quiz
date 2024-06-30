from dataclasses import dataclass
from core.services.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class QuestionDoesNotExists(BaseHTTPException):
    code: int = 400
    detail: str = "Такой вопрос не существует"
