"""Excel export: turn an optimization run into a KAYAK upload workbook.

Loads the *original* uploaded workbook and rewrites only the Override CPC cells
for routes whose recommended action is INCREASE. Every other action (KEEP,
MANUAL_REVIEW, INSUFFICIENT_DATA) and every route without a recommendation is
left untouched, so the file stays byte-identical apart from the bids that moved.

The recommendation engine is not consulted or modified here — this reads the
recommendations already persisted by :class:`OptimizationService`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.domain.enums import RecommendationAction
from app.models.optimization import BidRecommendation
from app.optimizer.config import DEFAULT_CONFIG, DeviceBidLimits
from app.optimizer.excel_export import BidUpdate, BidWorkbookExporter, optimized_filename
from app.optimizer.rules import device_for_provider
from app.repositories.bid_file_repository import BidFileRepository
from app.repositories.optimization_repository import (
    BidRecommendationRepository,
    OptimizationRunRepository,
)
from app.schemas.optimization import ExportSkippedRoute, ExportSummary

logger = get_logger("app.services.export")


@dataclass(frozen=True)
class ExportResult:
    """A generated workbook plus its summary, ready for an HTTP response."""

    filename: str
    content: bytes
    summary: ExportSummary


class ExportService:
    """Builds an optimized KAYAK workbook from a completed optimization run."""

    def __init__(self, session: AsyncSession) -> None:
        self._runs = OptimizationRunRepository(session)
        self._files = BidFileRepository(session)
        self._recs = BidRecommendationRepository(session)
        self._exporter = BidWorkbookExporter()

    async def build_export(self, run_id: int) -> ExportResult:
        run = await self._runs.get(run_id)
        if run is None:
            raise NotFoundError(f"optimization run {run_id} not found")

        bid_file = await self._files.get_with_content(run.bid_file_id)
        if bid_file is None:  # defensive: FK guarantees this normally
            raise NotFoundError(f"bid file {run.bid_file_id} not found")

        # Prefer the bytes persisted in the database; they survive the ephemeral
        # local disk being wiped on a container restart. Fall back to the on-disk
        # copy for rows uploaded before durable storage existed.
        source = bid_file.content
        if source is None:
            source = self._read_source(bid_file.stored_filename)
        recommendations = await self._recs.list_for_run(run_id)

        limits = DEFAULT_CONFIG.limits_for(device_for_provider(bid_file.provider_code))
        updates, diffs_by_key, skipped = self._plan_updates(
            recommendations, bid_file.provider_code, limits
        )

        result = self._exporter.apply_updates(source, updates)

        unmatched_keys = {
            (
                u.provider_code.strip().upper(),
                u.origin.strip().upper(),
                u.destination.strip().upper(),
            )
            for u in result.unmatched_updates
        }
        for update in result.unmatched_updates:
            skipped.append(
                ExportSkippedRoute(
                    origin=update.origin,
                    destination=update.destination,
                    reason="route not found in the original workbook",
                )
            )

        applied_diffs = [diff for key, diff in diffs_by_key.items() if key not in unmatched_keys]
        summary = ExportSummary(
            output_filename=optimized_filename(bid_file.original_filename),
            routes_processed=len(recommendations),
            routes_updated=result.rows_updated,
            routes_unchanged=len(recommendations) - result.rows_updated,
            manual_review_count=_count_action(recommendations, RecommendationAction.MANUAL_REVIEW),
            insufficient_data_count=_count_action(
                recommendations, RecommendationAction.INSUFFICIENT_DATA
            ),
            average_bid_increase=round(sum(applied_diffs) / len(applied_diffs), 2)
            if applied_diffs
            else 0.0,
            maximum_bid_increase=round(max(applied_diffs), 2) if applied_diffs else 0.0,
            skipped_routes=skipped,
            strategy_version=run.ruleset_version,
            timestamp=datetime.now(UTC),
        )
        logger.info(
            "export_built",
            run_id=run_id,
            updated=summary.routes_updated,
            unchanged=summary.routes_unchanged,
            skipped=len(summary.skipped_routes),
        )
        return ExportResult(
            filename=summary.output_filename, content=result.content, summary=summary
        )

    def _plan_updates(
        self,
        recommendations: list[BidRecommendation],
        provider_code: str,
        limits: DeviceBidLimits,
    ) -> tuple[list[BidUpdate], dict[tuple[str, str, str], float], list[ExportSkippedRoute]]:
        """Decide which routes get a new Override CPC. Only INCREASE writes a bid."""
        updates: list[BidUpdate] = []
        diffs_by_key: dict[tuple[str, str, str], float] = {}
        skipped: list[ExportSkippedRoute] = []

        for rec in recommendations:
            if rec.action is not RecommendationAction.INCREASE:
                continue  # KEEP / MANUAL_REVIEW / INSUFFICIENT_DATA -> leave unchanged
            bid = rec.recommended_bid
            if bid is None:  # defensive: an INCREASE always has a recommended bid
                skipped.append(_skip(rec, "increase recommendation is missing a recommended bid"))
                continue
            if not (limits.minimum <= bid <= limits.maximum):
                skipped.append(
                    _skip(
                        rec,
                        f"recommended bid {bid:.2f} is outside the allowed range "
                        f"{limits.minimum:.2f}-{limits.maximum:.2f}",
                    )
                )
                continue
            updates.append(
                BidUpdate(
                    provider_code=provider_code,
                    origin=rec.origin,
                    destination=rec.destination,
                    new_cpc=bid,
                )
            )
            key = (
                provider_code.strip().upper(),
                rec.origin.strip().upper(),
                rec.destination.strip().upper(),
            )
            diffs_by_key[key] = round(bid - (rec.current_bid or bid), 2)
        return updates, diffs_by_key, skipped

    @staticmethod
    def _read_source(stored_filename: str) -> bytes:
        path = Path(settings.UPLOAD_DIR) / stored_filename
        try:
            return path.read_bytes()
        except FileNotFoundError as exc:
            raise NotFoundError(
                "the original bid workbook is no longer available for export"
            ) from exc


def _count_action(recommendations: list[BidRecommendation], action: RecommendationAction) -> int:
    return sum(1 for rec in recommendations if rec.action is action)


def _skip(rec: BidRecommendation, reason: str) -> ExportSkippedRoute:
    return ExportSkippedRoute(origin=rec.origin, destination=rec.destination, reason=reason)
