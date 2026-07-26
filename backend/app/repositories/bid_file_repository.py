"""Data-access repositories for bid files and their routes."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import undefer

from app.models.bid_file import BidFile, BidFileRoute
from app.repositories.base import BaseRepository


class BidFileRepository(BaseRepository):
    """Persistence operations for bid files."""

    async def add(self, bid_file: BidFile) -> BidFile:
        self.session.add(bid_file)
        await self.session.flush()
        return bid_file

    async def get(self, bid_file_id: int) -> BidFile | None:
        return await self.session.get(BidFile, bid_file_id)

    async def get_with_content(self, bid_file_id: int) -> BidFile | None:
        """Load a bid file with its deferred ``content`` eagerly (for export).

        The blob is deferred so normal queries stay lean; export needs the bytes,
        and eager loading avoids an async lazy-load (which SQLAlchemy forbids).
        """
        result = await self.session.execute(
            select(BidFile).where(BidFile.id == bid_file_id).options(undefer(BidFile.content))
        )
        return result.scalar_one_or_none()

    async def get_by_checksum(self, checksum: str) -> BidFile | None:
        result = await self.session.execute(select(BidFile).where(BidFile.checksum == checksum))
        return result.scalar_one_or_none()

    async def list_page(self, *, limit: int, offset: int) -> list[BidFile]:
        result = await self.session.execute(
            select(BidFile).order_by(BidFile.uploaded_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(BidFile))
        return int(result.scalar_one())

    async def list_routes(self, bid_file_id: int) -> list[BidFileRoute]:
        result = await self.session.execute(
            select(BidFileRoute).where(BidFileRoute.bid_file_id == bid_file_id)
        )
        return list(result.scalars().all())


class BidFileRouteRepository(BaseRepository):
    """Bulk persistence for bid-file routes."""

    async def bulk_add(self, routes: Sequence[BidFileRoute]) -> None:
        if not routes:
            return
        self.session.add_all(list(routes))
        await self.session.flush()
