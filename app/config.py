from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno o .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Entorno
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)

    # HTTP Basic Auth (usuario único: Leo)
    app_username: str
    app_password: str
    secret_key: str

    # Base de datos PostgreSQL (asyncpg driver obligatorio)
    database_url: str

    # Anthropic Claude API (opcional hasta Sprint 7)
    anthropic_api_key: str = Field(default="")

    # Mercado Libre — opcional hasta Sprint 9
    ml_client_id: str = Field(default="")
    ml_client_secret: str = Field(default="")
    ml_refresh_token: str = Field(default="")

    # Google Books — opcional, fallback a Open Library si vacío
    google_books_api_key: str = Field(default="")

    # Reglas de negocio (configurables sin cambiar código)
    min_margin_cents: int = Field(default=5000)
    min_margin_pct: float = Field(default=20.0)

    # Scheduler
    scan_interval_hours: int = Field(default=4)

    # Logging
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna la instancia cacheada de Settings.

    La primera llamada crea el objeto leyendo env vars / .env.
    Si falta alguna variable obligatoria, Pydantic lanza ValidationError
    y la app no arranca — comportamiento intencional.
    """
    return Settings()
