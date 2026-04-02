"""String Free - AI-Assisted Build Control Platform.

Main FastAPI application entry point."""

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, opportunities, tasks, telegram, webhooks
from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown events."""
    logger.info("String Free starting up (env=%s)", settings.environment)
    yield
    logger.info("String Free shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Initialize Sentry if DSN is provided
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=1.0,
        )

    app = FastAPI(
        title="String Free Build",
        description="AI-Assisted Build Control Platform",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS for future web dashboard and Telegram Mini App
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            "%s %s → %s (%.3fs)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response

    # Register routes
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])

    return app


app = create_app()
