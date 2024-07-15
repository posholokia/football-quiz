import json
import uuid
from typing import Any

import aiohttp
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from core.services.firebase.conf import (
    JSON_CONF,
    REMOTE_CONFIG_URL,
    SCOPES,
)
from core.services.firebase.exceptions import (
    FirebaseGetConfigError,
    FirebaseGetEtagHeaderError,
)


async def _get_credentials() -> Credentials:
    credentials = Credentials.from_service_account_file(
        JSON_CONF, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials


async def _get_remote_config(cred: Credentials) -> tuple[Any, dict]:
    headers = {"Authorization": "Bearer " + cred.token}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            REMOTE_CONFIG_URL,
            headers=headers,
        ) as response:
            if response.status != 200:
                raise FirebaseGetConfigError()

            response_json = await response.json()
            response_headers = dict(response.headers)
        return response_json, response_headers


async def _get_etag_header(headers: dict) -> str:
    etag = headers.get("Etag")

    if etag is None:
        raise FirebaseGetEtagHeaderError()
    return etag


async def _get_api_key(response: Any) -> str:
    return response["parameters"]["api_key"]["defaultValue"]["value"]


async def _set_api_key(conf: dict) -> str:
    api_key = uuid.uuid4().hex
    conf["parameters"]["api_key"]["defaultValue"]["value"] = api_key
    return json.dumps(conf)


async def _set_new_conf(conf: str, cred: Credentials, etag: str) -> None:
    headers = {
        "Authorization": "Bearer " + cred.token,
        "Content-Type": "application/json; charset=UTF-8",
        "If-Match": etag,
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(
            REMOTE_CONFIG_URL,
            headers=headers,
            data=conf,
        ):
            pass
