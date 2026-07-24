"""Pytest fixtures.

Provides an in-process async HTTP client bound to the FastAPI app via httpx's
ASGI transport — no network, no running server required.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """An async HTTP client that drives the ASGI app directly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
