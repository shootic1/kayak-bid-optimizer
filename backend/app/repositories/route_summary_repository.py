"""Data-access repository for :class:`RouteSummary` aggregates."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import SupportsFloat, SupportsInt, cast

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.domain.enums import DeviceType
from app.models.performance_report import PerformanceReport
from app.models.route_summary import RouteSummary
from app.repositories.base import BaseRepository

RouteSegment = tuple[str, str, DeviceType]


@dataclass(frozen=True)
class RouteSummaryIndexRow:
    """A route summary projected for the optimization history index."""

    origin: str
    destination: str
    route_summary_id: int
    ctr: float | None
    avg_position: float | None
    spend: float | None
    clicks: int | None
    impressions: int | None
    bookings: int | None


def _opt_float(value: object) -> float | None:
    return None if value is None else float(cast("SupportsFloat", value))


def _opt_int(value: object) -> int | None:
    return None if value is None else int(cast("SupportsInt", value))


class RouteSummaryRepository(BaseRepository):
    """Recomputes and upserts per-route aggregate statistics."""

    async def load_index_rows(self) -> list[RouteSummaryIndexRow]:
        """Load all summaries for building a route-history index (one per summary)."""
        result = await self.session.execute(
            select(
                RouteSummary.origin,
                RouteSummary.destination,
                RouteSummary.id,
                RouteSummary.average_ctr,
                RouteSummary.average_position,
                RouteSummary.total_spend,
                RouteSummary.total_clicks,
                RouteSummary.total_impressions,
                RouteSummary.total_bookings,
            )
        )
        return [
            RouteSummaryIndexRow(
                origin=str(r[0]),
                destination=str(r[1]),
                route_summary_id=int(r[2]),
                ctr=_opt_float(r[3]),
                avg_position=_opt_float(r[4]),
                spend=_opt_float(r[5]),
                clicks=_opt_int(r[6]),
                impressions=_opt_int(r[7]),
                bookings=_opt_int(r[8]),
            )
            for r in result.all()
        ]

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
