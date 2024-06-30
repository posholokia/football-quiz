from core.services.constructor.exceptions import BaseHTTPException


class FirebaseInvalidApiKey(BaseHTTPException):
    code: int = 400
    detail: str = "Некорректный API_KEY"
