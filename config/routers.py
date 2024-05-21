from fastapi import APIRouter
from app.users.api import router as users_routers
from app.healthcheck.api import router as healthcheck_router

routers = APIRouter()

routers.include_router(users_routers)
routers.include_router(healthcheck_router)


