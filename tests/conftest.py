from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# Configurar env vars ANTES de importar cualquier módulo de la app.
# En CI estas variables vienen del environment del workflow.
# Localmente deben estar en .env o exportadas en la shell.
os.environ.setdefault("APP_USERNAME", "testuser")
os.environ.setdefault("APP_PASSWORD", "testpassword")
os.environ.setdefault("SECRET_KEY", "test-secret-key-min-32-chars-long-!!!")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test_arbitraje",
)
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("MIN_MARGIN_CENTS", "5000")
os.environ.setdefault("MIN_MARGIN_PCT", "20.0")
os.environ.setdefault("LOG_LEVEL", "WARNING")  # silenciar logs en tests


@pytest.fixture(scope="session", autouse=True)
def _clear_settings_cache() -> Generator[None, None, None]:
    """Limpia el cache de settings al inicio de la sesión de tests."""
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient de FastAPI para tests unitarios (sin BD real).

    init_db() crea el engine async pero no hace conexión real,
    por lo que los tests que no tocan BD funcionan sin Postgres.
    """
    from app.main import app

    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
