from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class CategoryComplaintDoesNotExists(BaseHTTPException):
    code: int = 400
    detail: str = "Такой категории не существует"
