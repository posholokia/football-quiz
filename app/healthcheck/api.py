from fastapi import APIRouter, Depends

from starlette import status


router = APIRouter()


@router.post("/healthcheck/", status_code=status.HTTP_200_OK)
async def health_check() -> None:
    """Сервисное API, проверка, что контейнер жив"""
    return None
