"""Optimization run orchestration: match routes, run the deterministic engine,
and store bid recommendations. Generates recommendations only — it never writes
to Excel or changes bids.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.domain.enums import (
    ConfidenceLevel,
    DeviceType,
    MatchStatus,
    RecommendationAction,
    RunStatus,
)
from app.models.bid_file import BidFile, BidFileRoute
from app.models.optimization import BidRecommendation, OptimizationRun, RuleResult
from app.optimizer.matching import BidRouteInput, RouteHistory, RouteMatcher
from app.optimizer.metrics import RouteMetrics
from app.optimizer.recommendation import Recommendation, RecommendationEngine
from app.optimizer.rules import RuleTrigger, device_for_provider
from app.repositories.bid_file_repository import BidFileRepository
from app.repositories.optimization_repository import (
    BidRecommendationRepository,
    OptimizationRunRepository,
)
from app.repositories.route_summary_repository import RouteSummaryRepository

logger = get_logger("app.services.optimization")

# Numeric proxy for the categorical confidence (kept for the existing float column
# and the min-confidence filter).
_CONFIDENCE_FLOAT = {
    ConfidenceLevel.HIGH: 1.0,
    ConfidenceLevel.MEDIUM: 0.66,
    ConfidenceLevel.LOW: 0.33,
}

# Non-matched routes are recorded but not optimized.
_NON_MATCHED = {
    MatchStatus.SKIPPED_EXCLUDED: (
        RecommendationAction.KEEP,
        RuleTrigger.EXCLUDED_ROUTE,
        "Route is excluded in the bid file; bid held.",
    ),
    MatchStatus.UNMATCHED_NO_HISTORY: (
        RecommendationAction.INSUFFICIENT_DATA,
        RuleTrigger.NO_HISTORY,
        "No historical performance for this route.",
    ),
    MatchStatus.UNMATCHED_NON_IATA: (
        RecommendationAction.INSUFFICIENT_DATA,
        RuleTrigger.NON_IATA_ROUTE,
        "Origin/Destination is not a 3-letter IATA code.",
    ),
}


class OptimizationService:
    """Runs the deterministic recommendation engine over a bid file's routes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._files = BidFileRepository(session)
        self._runs = OptimizationRunRepository(session)
        self._recs = BidRecommendationRepository(session)
        self._summaries = RouteSummaryRepository(session)
        self._engine = RecommendationEngine()

    async def run(self, bid_file_id: int) -> OptimizationRun:
        bid_file = await self._files.get(bid_file_id)
        if bid_file is None:
            raise NotFoundError(f"bid file {bid_file_id} not found")

        routes = await self._files.list_routes(bid_file_id)
        run = OptimizationRun(
            bid_file_id=bid_file_id,
            status=RunStatus.RUNNING,
            ruleset_version=self._engine.config_version,
            total_routes=len(routes),
        )
        await self._runs.add(run)

        start = time.perf_counter()
        try:
            await self._execute(run, bid_file, routes)
        except Exception as exc:  # defensive: never leave a run stuck RUNNING
            logger.error("optimization_failed", run_id=run.id, error=str(exc), exc_info=exc)
            run.status = RunStatus.FAILED
            run.error_message = str(exc)
            run.finished_at = datetime.now(UTC)
            await self._session.flush()
            return run

        logger.info(
            "optimization_completed",
            run_id=run.id,
            matched=run.matched_count,
            unmatched=run.unmatched_count,
            skipped=run.skipped_count,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )
        return run

    async def _execute(
        self, run: OptimizationRun, bid_file: BidFile, routes: list[BidFileRoute]
    ) -> None:
        matcher = RouteMatcher(await self._build_history_index())
        device = device_for_provider(bid_file.provider_code)
        prior_failed = await self._recs.failed_position_counts()

        recommendations: list[BidRecommendation] = []
        matched = unmatched = skipped = 0

        for route in routes:
            outcome = matcher.match(BidRouteInput(route.origin, route.destination, route.excluded))
            if outcome.status is MatchStatus.MATCHED:
                matched += 1
                result = self._engine.recommend(
                    device=device,
                    current_bid=route.current_override_cpc,
                    metrics=outcome.metrics or RouteMetrics(),
                    prior_failed_runs=prior_failed.get((route.origin, route.destination), 0),
                )
                recommendations.append(
                    self._to_row(run.id, route, outcome.status, outcome.route_summary_id, result)
                )
            else:
                if outcome.status is MatchStatus.SKIPPED_EXCLUDED:
                    skipped += 1
                else:
                    unmatched += 1
                recommendations.append(self._non_matched_row(run.id, route, outcome.status, device))

        await self._recs.bulk_add(recommendations)
        await self._persist_rule_results(recommendations)

        run.matched_count = matched
        run.unmatched_count = unmatched
        run.skipped_count = skipped
        run.recommendation_count = matched
        run.status = RunStatus.COMPLETED
        run.finished_at = datetime.now(UTC)
        await self._session.flush()

    @staticmethod
    def _to_row(
        run_id: int,
        route: BidFileRoute,
        status: MatchStatus,
        route_summary_id: int | None,
        result: Recommendation,
    ) -> BidRecommendation:
        return BidRecommendation(
            optimization_run_id=run_id,
            bid_file_route_id=route.id,
            route_summary_id=route_summary_id,
            match_status=status,
            origin=route.origin,
            destination=route.destination,
            device=result.device,
            action=result.action,
            rule_triggered=result.rule_triggered,
            confidence_level=result.confidence,
            manual_review=result.manual_review,
            current_bid=result.current_bid,
            recommended_bid=result.recommended_bid,
            difference=result.difference,
            pct_change=result.pct_change,
            current_position=result.current_position,
            ctr=result.ctr,
            clicks=result.clicks,
            impressions=result.impressions,
            spend=result.spend,
            confidence=_CONFIDENCE_FLOAT[result.confidence],
            reason=result.reason,
        )

    @staticmethod
    def _non_matched_row(
        run_id: int, route: BidFileRoute, status: MatchStatus, device: DeviceType
    ) -> BidRecommendation:
        action, trigger, reason = _NON_MATCHED[status]
        return BidRecommendation(
            optimization_run_id=run_id,
            bid_file_route_id=route.id,
            route_summary_id=None,
            match_status=status,
            origin=route.origin,
            destination=route.destination,
            device=device,
            action=action,
            rule_triggered=trigger.value,
            confidence_level=ConfidenceLevel.LOW,
            manual_review=False,
            current_bid=route.current_override_cpc,
            recommended_bid=route.current_override_cpc,
            difference=0.0 if route.current_override_cpc is not None else None,
            pct_change=0.0 if route.current_override_cpc is not None else None,
            confidence=_CONFIDENCE_FLOAT[ConfidenceLevel.LOW],
            reason=reason,
        )

    async def _persist_rule_results(self, recommendations: list[BidRecommendation]) -> None:
        """Store one rule result per matched recommendation (the triggering rule)."""
        rows: list[dict[str, object]] = [
            {
                "bid_recommendation_id": rec.id,
                "rule_key": rec.rule_triggered or "",
                "rule_version": self._engine.config_version,
                "triggered": True,
                "weight": 0.0,
                "signal": rec.pct_change or 0.0,
                "detail": {
                    "action": rec.action.value,
                    "position": rec.current_position,
                    "ctr": rec.ctr,
                    "clicks": rec.clicks,
                    "impressions": rec.impressions,
                    "spend": rec.spend,
                    "confidence": rec.confidence_level.value if rec.confidence_level else None,
                    "manual_review": rec.manual_review,
                },
            }
            for rec in recommendations
            if rec.match_status is MatchStatus.MATCHED
        ]
        if rows:
            await self._session.execute(insert(RuleResult), rows)

    async def _build_history_index(self) -> dict[tuple[str, str], RouteHistory]:
        """Build a deterministic ``(origin, destination) -> history`` index."""
        index: dict[tuple[str, str], RouteHistory] = {}
        for row in await self._summaries.load_index_rows():
            key = (row.origin.upper(), row.destination.upper())
            if key in index:
                continue  # first wins; data is unique per (origin, destination)
            index[key] = RouteHistory(
                route_summary_id=row.route_summary_id,
                metrics=RouteMetrics(
                    ctr=row.ctr,
                    avg_position=row.avg_position,
                    spend=row.spend,
                    clicks=row.clicks,
                    impressions=row.impressions,
                    bookings=row.bookings,
                ),
            )
        return index

    async def get_run(self, run_id: int) -> OptimizationRun:
        run = await self._runs.get(run_id)
        if run is None:
            raise NotFoundError(f"optimization run {run_id} not found")
        return run

    async def list_runs(self, *, limit: int, offset: int) -> tuple[list[OptimizationRun], int]:
        runs = await self._runs.list_page(limit=limit, offset=offset)
        total = await self._runs.count()
        return runs, total
