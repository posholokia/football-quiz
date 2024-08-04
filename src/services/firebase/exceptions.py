from dataclasses import dataclass

from core.constructor.exceptions import BaseHTTPException


@dataclass(eq=False)
class FirebaseInvalidApiKey(BaseHTTPException):
    code: int = 400
    detail: str = "Некорректный API_KEY"


@dataclass(eq=False)
class FirebaseGetConfigError(BaseHTTPException):
    code: int = 503
    detail: str = "Не удалось загрузить RemoteConfig из Firebase"


@dataclass(eq=False)
class FirebaseGetEtagHeaderError(BaseHTTPException):
    code: int = 503
    detail: str = "Не удалось получить заголовок Etag из ответа Firebase"


@dataclass(eq=False)
class FirebaseRemoteConfigError(BaseHTTPException):
    code: int = 503
    detail: str = "Ошибка обработки Firebase RemoteConfig"
