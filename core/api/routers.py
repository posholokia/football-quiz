from fastapi import APIRouter
from starlette import status
from .mobile.game_settings import router as game_router
from .mobile.quiz import router as quiz_router
from .mobile.users import router as users_routers


routers = APIRouter()

routers.include_router(users_routers, tags=["Users"])
routers.include_router(quiz_router, tags=["Quiz"])
routers.include_router(game_router, tags=["Settings"])


@routers.get("/healthcheck/", status_code=status.HTTP_200_OK)
async def health_check() -> None:
    """Сервисное API, проверка, что контейнер жив"""
    return None
