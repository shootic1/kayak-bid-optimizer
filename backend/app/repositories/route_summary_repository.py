"""Data-access repository for :class:`RouteSummary` aggregates."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domain.enums import DeviceType
from app.models.performance_report import PerformanceReport
from app.models.route_summary import RouteSummary
from app.repositories.base import BaseRepository

RouteSegment = tuple[str, str, DeviceType]


class RouteSummaryRepository(BaseRepository):
    """Recomputes and upserts per-route aggregate statistics."""

    async def recompute_segments(self, segments: Iterable[RouteSegment]) -> None:
        """Recompute the summary for each ``(origin, destination, device)`` segment.

        Aggregates over ALL performance rows for the segment so summaries stay
        correct across multiple uploads and after deletions. A segment with no
        remaining rows has its summary removed.
        """
        for origin, destination, device in set(segments):
            await self._recompute_segment(origin, destination, device)

    async def _recompute_segment(self, origin: str, destination: str, device: DeviceType) -> None:
        where = (
            PerformanceReport.origin == origin,
            PerformanceReport.destination == destination,
            PerformanceReport.device == device,
        )
        result = await self.session.execute(
            select(
                func.count().label("total_reports"),
                func.coalesce(func.sum(PerformanceReport.impressions), 0),
                func.coalesce(func.sum(PerformanceReport.clicks), 0),
                func.coalesce(func.sum(PerformanceReport.spend), 0),
                func.coalesce(func.sum(PerformanceReport.bookings), 0),
                func.max(PerformanceReport.report_date),
                func.avg(PerformanceReport.avg_position),
            ).where(*where)
        )
        row = result.one()
        total_reports = int(row[0])

        if total_reports == 0:
            await self.session.execute(
                delete(RouteSummary).where(
                    RouteSummary.origin == origin,
                    RouteSummary.destination == destination,
                    RouteSummary.device == device,
                )
            )
            return

        total_impressions = int(row[1])
        total_clicks = int(row[2])
        total_spend = float(row[3])
        total_bookings = int(row[4])
        last_report_date = row[5]
        avg_position = float(row[6]) if row[6] is not None else None

        values = {
            "origin": origin,
            "destination": destination,
            "device": device,
            "total_reports": total_reports,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "average_ctr": (total_clicks / total_impressions) if total_impressions else None,
            "average_cpc": (total_spend / total_clicks) if total_clicks else None,
            "average_position": avg_position,
            "total_spend": total_spend,
            "total_bookings": total_bookings,
            "last_report_date": last_report_date,
        }
        stmt = pg_insert(RouteSummary).values(**values)
        update_cols = {
            k: stmt.excluded[k] for k in values if k not in ("origin", "destination", "device")
        }
        stmt = stmt.on_conflict_do_update(constraint="uq_route_summary_segment", set_=update_cols)
        await self.session.execute(stmt)
