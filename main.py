from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.api.routers import routers
from core.config.settings import DEBUG
from core.services.constructor.exceptions import BaseHTTPException


def create_app() -> FastAPI:
    app = FastAPI(
        title="Football Quiz",
        docs_url="/api/docs",
        description="Mobile application",
        debug=DEBUG,
    )

    @app.exception_handler(BaseHTTPException)
    async def custom_http_exception_handler(request: Request, exc: BaseHTTPException):
        return JSONResponse(
            status_code=exc.code,
            content={"detail": exc.detail},
        )
    app.include_router(routers, prefix="/api/v1")
    return app
