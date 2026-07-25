"""Unit tests for database URL normalization."""

from __future__ import annotations

import pytest

from app.database.url import normalize_async_database_url


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # Railway-style bare DSN is upgraded to the asyncpg driver.
        (
            "postgresql://user:pass@host:5432/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
        ),
        # Already-async DSN is left untouched.
        (
            "postgresql+asyncpg://user:pass@host:5432/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
        ),
        # Only the leading scheme is rewritten, not later occurrences.
        (
            "postgresql://u:postgresql://@host/db",
            "postgresql+asyncpg://u:postgresql://@host/db",
        ),
        # Other explicit drivers are preserved.
        (
            "postgresql+psycopg://user:pass@host/db",
            "postgresql+psycopg://user:pass@host/db",
        ),
    ],
)
def test_normalize_async_database_url(given: str, expected: str) -> None:
    assert normalize_async_database_url(given) == expected


def test_normalize_is_idempotent() -> None:
    once = normalize_async_database_url("postgresql://user:pass@host/db")
    assert normalize_async_database_url(once) == once
