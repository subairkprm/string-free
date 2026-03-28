"""String Free - AI-Assisted Build Control Platform.

Main FastAPI application entry point."""

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import settings


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
    )

    # CORS for future web dashboard and Telegram Mini App
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router, prefix="/health", tags=["health"])

    return app


app = create_app()
