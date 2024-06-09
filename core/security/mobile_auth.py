from typing import Optional

from pydantic.main import BaseModel

from fastapi import Request
from fastapi.openapi.models import APIKey
from fastapi.security.base import SecurityBase


api_key_scheme = {
    "name": "Device",
    "in": "header",
}


class MobileAuthorizationCredentials(BaseModel):
    type: str
    token: str


class HTTPDevice(SecurityBase):
    def __init__(self, scheme_name: Optional[str] = None):
        self.model = APIKey(**api_key_scheme)
        self.scheme_name = scheme_name or self.__class__.__name__

    async def __call__(
        self, request: Request
    ) -> Optional[MobileAuthorizationCredentials]:
        device_auth = request.headers.get("Device")
        if not device_auth:
            return None
        return MobileAuthorizationCredentials(type="device", token=device_auth)
