"""Async database engine and session management.

Exposes a lazily-created async engine, a session factory, and a FastAPI
dependency (``get_db_session``) that yields a scoped ``AsyncSession`` per
request. The engine is created once and disposed on application shutdown via the
lifespan handler in ``app.main``.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.database")

# Module-level singletons, initialised on first access.
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the process-wide async engine, creating it on first use."""
    global _engine
    if _engine is None:
        logger.info("database_engine_create", pool_size=settings.DB_POOL_SIZE)
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            connect_args={"timeout": settings.DB_CONNECT_TIMEOUT_SECONDS},
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide session factory, creating it on first use."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped ``AsyncSession``.

    The session is rolled back and closed automatically when the request ends.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Dispose of the engine and its connection pool (call on shutdown)."""
    global _engine, _session_factory
    if _engine is not None:
        logger.info("database_engine_dispose")
        await _engine.dispose()
        _engine = None
        _session_factory = None
