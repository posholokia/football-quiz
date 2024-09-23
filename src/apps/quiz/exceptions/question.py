from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class QuestionDoesNotExists(BaseHTTPException):
    code: int = 400
    detail: str = "Такой вопрос не существует"


@dataclass(eq=False)
class QuestionIntegrityError(BaseHTTPException):
    code: int = 409
    detail: str = "Невозможно сохранить эти вопросы"
