from fastapi import APIRouter
from starlette import status

from .admin.auth.handlers import router as auth_admin_router
from .admin.game_settings.handlers import router as game_settings_router
from .admin.quiz.handlers import router as quiz_admin_router
from .admin.users.handlers import router as users_admin_router
from .mobile.game_settings.handlers import router as game_router
from .mobile.quiz.handlers import router as quiz_router
from .mobile.users.handlers import router as users_routers
from .web.users.handlers import router as web_users_router


routers = APIRouter()

routers.include_router(users_routers, tags=["Mobile"])
routers.include_router(quiz_router, tags=["Mobile"])
routers.include_router(game_router, tags=["Mobile"])

routers.include_router(auth_admin_router, tags=["Admin"])
routers.include_router(game_settings_router, tags=["Admin"])
routers.include_router(quiz_admin_router, tags=["Admin"])
routers.include_router(users_admin_router, tags=["Admin"])

routers.include_router(web_users_router, tags=["Web"])


@routers.get("/healthcheck/", status_code=status.HTTP_200_OK)
async def health_check() -> None:
    """Сервисное API, проверка, что контейнер жив"""
    return None
