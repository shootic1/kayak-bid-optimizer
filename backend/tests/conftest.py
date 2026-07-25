"""Pytest fixtures.

Integration tests run against the application's configured PostgreSQL database
(``DATABASE_URL``), which must already be migrated (``alembic upgrade head``).
Each test starts from a clean slate via truncation, and uploads are written to a
temporary directory.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import app.models
from app.core.config import settings
from app.database.session import dispose_engine, get_session_factory
from app.main import app

_TABLES = ("performance_reports", "uploads", "route_summaries")


@pytest.fixture(scope="session", autouse=True)
def _upload_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Redirect uploaded-file storage to a temporary directory for the test session."""
    tmp = tmp_path_factory.mktemp("uploads")
    settings.UPLOAD_DIR = str(tmp)
    return tmp


@pytest.fixture(autouse=True)
async def _clean_db() -> AsyncIterator[None]:
    """Truncate ingestion tables before each test and dispose the engine after.

    Disposing at teardown resets the lazily-created async engine so each test
    binds a fresh engine to its own event loop (pytest-asyncio uses a per-test
    loop), avoiding cross-loop reuse errors.
    """
    factory = get_session_factory()
    async with factory() as session:
        await session.execute(text(f"TRUNCATE {', '.join(_TABLES)} RESTART IDENTITY CASCADE"))
        await session.commit()
    yield
    await dispose_engine()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """A session for asserting database state within a test."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """An async HTTP client that drives the ASGI app directly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
