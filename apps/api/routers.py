from fastapi import APIRouter
from .mobile.users import router as users_routers
from .mobile.quiz import router as quiz_router
from starlette import status

routers = APIRouter()

routers.include_router(users_routers)
routers.include_router(quiz_router)


@routers.get("/healthcheck/", status_code=status.HTTP_200_OK)
async def health_check() -> None:
    """Сервисное API, проверка, что контейнер жив"""
    return None
