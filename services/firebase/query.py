import aiohttp
from aiohttp.client_reqrep import ClientResponse
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from fastapi import HTTPException

from services.firebase.conf import (
    JSON_CONF,
    REMOTE_CONFIG_URL,
    SCOPES,
)


async def _get_credentials() -> Credentials:
    credentials = Credentials.from_service_account_file(
        JSON_CONF, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials


async def _get_remote_config() -> ClientResponse:
    cred = await _get_credentials()
    headers = {"Authorization": "Bearer " + cred.token}
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            REMOTE_CONFIG_URL,
            headers=headers,
        )
        if response.status != 200:
            raise HTTPException(
                status_code=503,
                detail="Не удалось загрузить RemoteConfig из Firebase",
            )
        return response


async def _get_etag_header(response: ClientResponse) -> str:
    headers = response.headers
    etag = headers.get("Etag")

    if etag is None:
        raise HTTPException(
            status_code=503,
            detail="Не удалось получить заголовок Etag из ответа Firebase",
        )
    return etag


async def _get_api_key(response: ClientResponse) -> str:
    response_json = await response.json()
    return response_json["parameters"]["api_key"]["defaultValue"]["value"]
