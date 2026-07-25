"""Data-access repository for :class:`PerformanceReport`."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select

from app.domain.enums import DeviceType
from app.models.performance_report import PerformanceReport
from app.repositories.base import BaseRepository


class PerformanceReportRepository(BaseRepository):
    """Persistence operations for performance report rows."""

    async def bulk_add(self, reports: Sequence[PerformanceReport]) -> None:
        """Insert many report rows in one flush."""
        if not reports:
            return
        self.session.add_all(list(reports))
        await self.session.flush()

    async def segments_for_upload(self, upload_id: int) -> set[tuple[str, str, DeviceType]]:
        """Return the distinct ``(origin, destination, device)`` segments of an upload."""
        result = await self.session.execute(
            select(
                PerformanceReport.origin,
                PerformanceReport.destination,
                PerformanceReport.device,
            )
            .where(PerformanceReport.upload_id == upload_id)
            .distinct()
        )
        return {(origin, destination, device) for origin, destination, device in result.all()}
