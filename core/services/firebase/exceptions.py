from core.services.constructor.exceptions import BaseHTTPException


class FirebaseInvalidApiKey(BaseHTTPException):
    code: int = 400
    detail: str = "Некорректный API_KEY"


class FirebaseGetConfigError(BaseHTTPException):
    code: int = 500
    detail: str = "Не удалось загрузить RemoteConfig из Firebase"


class FirebaseGetEtagHeaderError(BaseHTTPException):
    code: int = 500
    detail: str = "Не удалось получить заголовок Etag из ответа Firebase"


class FirebaseRemoteConfigError(BaseHTTPException):
    code: int = 500
    detail: str = "Ошибка обработки Firebase RemoteConfig"
