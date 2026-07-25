"""Data-access repository for :class:`Upload`."""

from __future__ import annotations

from sqlalchemy import func, select

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository):
    """Persistence operations for uploads."""

    async def add(self, upload: Upload) -> Upload:
        self.session.add(upload)
        await self.session.flush()
        return upload

    async def get(self, upload_id: int) -> Upload | None:
        return await self.session.get(Upload, upload_id)

    async def get_by_checksum(self, checksum: str) -> Upload | None:
        result = await self.session.execute(select(Upload).where(Upload.checksum == checksum))
        return result.scalar_one_or_none()

    async def list(self, *, limit: int, offset: int) -> list[Upload]:
        result = await self.session.execute(
            select(Upload).order_by(Upload.uploaded_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Upload))
        return int(result.scalar_one())

    async def delete(self, upload: Upload) -> None:
        await self.session.delete(upload)
        await self.session.flush()
