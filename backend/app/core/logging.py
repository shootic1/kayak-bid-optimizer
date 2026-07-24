"""Structured logging configuration.

Uses ``structlog`` to emit either human-friendly console logs (development) or
machine-parseable JSON (production/log aggregators). Standard-library logging is
routed through the same processor chain so third-party libraries (uvicorn,
SQLAlchemy) share one consistent format.
"""

from __future__ import annotations

import logging
import sys

import structlog

from app.core.config import settings

# Shared processors applied to both structlog and stdlib log records.
_SHARED_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def configure_logging() -> None:
    """Configure structlog + stdlib logging for the whole process.

    Idempotent: safe to call once at application startup.
    """
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.LOG_FORMAT == "json"
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    structlog.configure(
        processors=[
            *_SHARED_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_SHARED_PROCESSORS,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Align noisy third-party loggers with our root configuration.
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(logger_name).handlers = []
        logging.getLogger(logger_name).propagate = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger, optionally namespaced by ``name``."""
    return structlog.stdlib.get_logger(name) if name else structlog.stdlib.get_logger()
