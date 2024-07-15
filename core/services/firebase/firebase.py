from core.services.firebase.exceptions import FirebaseInvalidApiKey
from core.services.firebase.query import (
    _get_api_key,
    _get_credentials,
    _get_etag_header,
    _get_remote_config,
    _set_api_key,
    _set_new_conf,
)


async def check_firebase_apikey(api_key: str) -> None:
    credentials = await _get_credentials()
    remote_config, _ = await _get_remote_config(credentials)
    remote_api_key = await _get_api_key(remote_config)

    if api_key != remote_api_key:
        raise FirebaseInvalidApiKey()


async def change_api_key() -> None:
    credentials = await _get_credentials()
    config, header = await _get_remote_config(credentials)
    new_conf = await _set_api_key(config)
    etag = await _get_etag_header(header)
    await _set_new_conf(new_conf, credentials, etag)
