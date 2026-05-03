from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.dashboard import router as _dashboard_router
from app.api.v1.books import router as _books_router
from app.api.v1.opportunities import router as _opp_router
from app.api.v1.publications import router as _pub_router
from app.config import get_settings
from app.core.logging_config import configure_logging
from app.database import close_db, init_db

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la app: startup y shutdown."""
    settings = get_settings()
    configure_logging(log_level=settings.log_level, log_json=settings.log_json)
    init_db(settings.database_url, debug=settings.debug)
    logger.info("app_startup", env=settings.app_env, version=app.version)
    yield
    await close_db()
    logger.info("app_shutdown")


app = FastAPI(
    title="Arbitraje de Libros",
    description="Detección de oportunidades de arbitraje de libros usados en ML México.",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(_dashboard_router)
app.include_router(_opp_router, prefix="/api/v1")
app.include_router(_books_router, prefix="/api/v1")
app.include_router(_pub_router, prefix="/api/v1")


@app.get("/health", tags=["sistema"])
async def health() -> dict[str, str]:
    """Healthcheck del servicio. Railway pinguea este endpoint cada 30s."""
    return {"status": "ok"}


@app.get("/version", tags=["sistema"])
async def version_endpoint() -> dict[str, str]:
    """Versión y entorno de la aplicación."""
    settings = get_settings()
    return {"version": app.version, "env": settings.app_env}
