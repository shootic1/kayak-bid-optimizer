"""FastAPI application entrypoint.

Wires configuration, structured logging, CORS, global exception handlers, the
composed API router, and a lifespan that disposes the database engine on
shutdown. Exposes ``app`` for ``uvicorn app.main:app``.
"""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.database.session import dispose_engine

logger = get_logger("app.main")


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and graceful shutdown."""
    configure_logging()
    logger.info(
        "application_startup",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.NODE_ENV,
    )
    try:
        yield
    finally:
        await dispose_engine()
        logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Application factory — build and configure the FastAPI instance."""
    configure_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    return app


app = create_app()
