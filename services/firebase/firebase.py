from fastapi import HTTPException

from .query import (
    _get_api_key,
    _get_remote_config,
)


async def check_firebase_apikey(api_key: str) -> None:
    remote_config = await _get_remote_config()
    remote_api_key = await _get_api_key(remote_config)

    if api_key != remote_api_key:
        raise HTTPException(
            status_code=400,
            detail="Некорректный API_KEY",
        )
