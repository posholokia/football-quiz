from fastapi import FastAPI

from apps.api.routers import routers
from config.settings import DEBUG


def create_app() -> FastAPI:
    app = FastAPI(
        title="Football Quiz",
        docs_url="/api/docs",
        description="Mobile application",
        debug=DEBUG,
    )
    app.include_router(routers, prefix="/api/v1")
    return app
