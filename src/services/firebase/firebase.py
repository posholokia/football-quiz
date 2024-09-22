from loguru import logger

from config import settings
from services.firebase.exceptions import FirebaseInvalidApiKey
from services.firebase.query import (
    _get_api_key,
    _get_credentials,
    _get_etag_header,
    _get_remote_config,
    _set_api_key,
    _set_new_conf,
)


async def check_firebase_apikey(api_key: str) -> None:
    if settings.environ != "prod":
        return

    credentials = await _get_credentials()
    remote_config, _ = await _get_remote_config(credentials)
    remote_api_key = _get_api_key(remote_config)

    if api_key != remote_api_key:
        logger.debug(
            "Получен невалидный api_key: {} != {}", api_key, remote_api_key
        )
        raise FirebaseInvalidApiKey()


async def change_api_key() -> None:
    credentials = await _get_credentials()
    config, header = await _get_remote_config(credentials)
    new_conf = _set_api_key(config)
    etag = _get_etag_header(header)
    await _set_new_conf(new_conf, credentials, etag)


if __name__ == "__main__":
    import asyncio

    asyncio.run(check_firebase_apikey("qwrert1234"))
