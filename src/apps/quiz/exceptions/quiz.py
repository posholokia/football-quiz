from dataclasses import dataclass

from services.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class QuestionDoesNotExists(BaseHTTPException):
    code: int = 400
    detail: str = "Такой вопрос не существует"


@dataclass(eq=False)
class CategoryComplaintDoesNotExists(BaseHTTPException):
    code: int = 400
    detail: str = "Такой категории не существует"
