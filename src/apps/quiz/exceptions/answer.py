from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class AnswerRightVariableError(BaseHTTPException):
    code: int = 400
    detail: str = "Некорректное количество правильных вариантов ответа"


@dataclass(eq=False)
class AnswerNotUniqueError(BaseHTTPException):
    code: int = 400
    detail: str = "Варианты ответа повторяются"


@dataclass(eq=False)
class AnswerNotEnoughError(BaseHTTPException):
    code: int = 400
    detail: str = "Должно быть 4 варианта ответа"
