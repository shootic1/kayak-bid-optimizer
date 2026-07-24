"""Generic repository base class.

Establishes the repository pattern boundary between the service layer and
SQLAlchemy. Concrete repositories (added in future phases) subclass this to get a
session handle and a consistent constructor. No queries are implemented in
Phase 1 because there are no business models yet.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base class for data-access repositories.

    Subclasses receive an :class:`AsyncSession` and expose intent-revealing
    methods (``get``, ``list``, ``create`` ...) so the service layer never issues
    raw queries directly.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session
