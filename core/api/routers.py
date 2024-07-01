from fastapi import APIRouter

from .mobile.game_settings import router as game_router
from .mobile.quiz import router as quiz_router
from .mobile.users import router as users_routers


routers = APIRouter()

routers.include_router(users_routers, tags=["Users"])
routers.include_router(quiz_router, tags=["Quiz"])
routers.include_router(game_router, tags=["Settings"])
