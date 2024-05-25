from fastapi import APIRouter
from mobile.users.api import router as users_routers
from healthcheck.api import router as healthcheck_router
from mobile.quiz.api import router as quiz_router

routers = APIRouter()

routers.include_router(users_routers)
routers.include_router(healthcheck_router)
routers.include_router(quiz_router)
