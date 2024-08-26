from api.routers import routers

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from core.constructor.exceptions import BaseHTTPException


def create_app() -> FastAPI:
    app = FastAPI(
        title="Football Quiz",
        docs_url="/api/docs",
        description="Mobile application",
        debug=settings.debug,
    )

    @app.exception_handler(BaseHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: BaseHTTPException
    ):
        return JSONResponse(
            status_code=exc.code,
            content={"detail": exc.detail},
        )

    origins = [
        "https://football-quiz.fun",
        "https://www.football-quiz.fun",
        "https://admin.football-quiz.fun;",
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routers, prefix="/api/v1")
    return app
