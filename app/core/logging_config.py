from __future__ import annotations

import logging
from typing import Any

import structlog


def configure_logging(*, log_level: str = "INFO", log_json: bool = False) -> None:
    """Configura structlog para la aplicación.

    Args:
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_json: Si True, emite JSON (producción). Si False, consola legible (dev).
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]

    renderer: Any
    if log_json:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=level,
    )
