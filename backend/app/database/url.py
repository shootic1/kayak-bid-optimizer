"""Database URL normalization helpers.

Some platforms (e.g. Railway) inject a bare ``postgresql://`` DSN. SQLAlchemy's
async engine requires an explicit async driver in the scheme, so the URL must be
rewritten to ``postgresql+asyncpg://`` before ``create_async_engine`` is called.
"""

from __future__ import annotations

_SYNC_PREFIX = "postgresql://"
_ASYNC_PREFIX = "postgresql+asyncpg://"


def normalize_async_database_url(url: str) -> str:
    """Ensure a PostgreSQL DSN uses the asyncpg driver.

    - ``postgresql://...``          -> ``postgresql+asyncpg://...``
    - ``postgresql+asyncpg://...``  -> returned unchanged
    - any other scheme              -> returned unchanged

    Only the leading scheme is rewritten (``replace(..., 1)`` semantics), so a
    ``postgresql://`` occurring later in the DSN (e.g. inside a password) is not
    affected.
    """
    if url.startswith(_ASYNC_PREFIX):
        return url
    if url.startswith(_SYNC_PREFIX):
        return _ASYNC_PREFIX + url[len(_SYNC_PREFIX) :]
    return url
