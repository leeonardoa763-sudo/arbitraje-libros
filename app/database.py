from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str, *, debug: bool = False) -> None:
    """Inicializa el engine async y la session factory.

    Llamar una sola vez al arrancar la app (en el lifespan de FastAPI).
    No hace conexión real — solo crea los objetos de SQLAlchemy.
    """
    global _engine, _session_factory
    _engine = create_async_engine(
        database_url,
        echo=debug,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def close_db() -> None:
    """Cierra el engine y libera conexiones del pool al apagar la app."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI que provee una AsyncSession por request."""
    if _session_factory is None:
        raise RuntimeError("BD no inicializada. Llamar a init_db() primero.")
    async with _session_factory() as session:
        yield session
