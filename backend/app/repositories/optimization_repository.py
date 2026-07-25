"""Data-access repositories for optimization runs and recommendations."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.domain.enums import MatchStatus
from app.models.optimization import BidRecommendation, OptimizationRun, RuleResult
from app.repositories.base import BaseRepository


class OptimizationRunRepository(BaseRepository):
    """Persistence operations for optimization runs."""

    async def add(self, run: OptimizationRun) -> OptimizationRun:
        self.session.add(run)
        await self.session.flush()
        return run

    async def get(self, run_id: int) -> OptimizationRun | None:
        return await self.session.get(OptimizationRun, run_id)

    async def list_page(self, *, limit: int, offset: int) -> list[OptimizationRun]:
        result = await self.session.execute(
            select(OptimizationRun)
            .order_by(OptimizationRun.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(OptimizationRun))
        return int(result.scalar_one())


class BidRecommendationRepository(BaseRepository):
    """Persistence and querying for bid recommendations."""

    async def bulk_add(self, recommendations: Sequence[BidRecommendation]) -> None:
        if not recommendations:
            return
        self.session.add_all(list(recommendations))
        await self.session.flush()

    async def failed_position_counts(self) -> dict[tuple[str, str], int]:
        """Count prior matched recommendations where the route stayed at position > 1.

        Used to detect routes that repeatedly fail to reach Position #1. Excludes
        the current run (its recommendations are not yet inserted).
        """
        result = await self.session.execute(
            select(
                BidRecommendation.origin,
                BidRecommendation.destination,
                func.count(),
            )
            .where(
                BidRecommendation.match_status == MatchStatus.MATCHED,
                BidRecommendation.current_position > 1.0,
            )
            .group_by(BidRecommendation.origin, BidRecommendation.destination)
        )
        return {(origin, destination): int(count) for origin, destination, count in result.all()}

    async def list_for_run(self, run_id: int) -> list[BidRecommendation]:
        """All recommendations for a run, ordered deterministically (for export)."""
        result = await self.session.execute(
            select(BidRecommendation)
            .where(BidRecommendation.optimization_run_id == run_id)
            .order_by(BidRecommendation.id)
        )
        return list(result.scalars().all())

    async def get_with_rules(self, recommendation_id: int) -> BidRecommendation | None:
        result = await self.session.execute(
            select(BidRecommendation)
            .where(BidRecommendation.id == recommendation_id)
            .options(selectinload(BidRecommendation.rule_results))
        )
        return result.scalar_one_or_none()

    async def list_page(
        self,
        *,
        limit: int,
        offset: int,
        run_id: int | None = None,
        status: MatchStatus | None = None,
        min_confidence: float | None = None,
    ) -> tuple[list[BidRecommendation], int]:
        conditions = []
        if run_id is not None:
            conditions.append(BidRecommendation.optimization_run_id == run_id)
        if status is not None:
            conditions.append(BidRecommendation.match_status == status)
        if min_confidence is not None:
            conditions.append(BidRecommendation.confidence >= min_confidence)

        base = select(BidRecommendation)
        count_stmt = select(func.count()).select_from(BidRecommendation)
        for cond in conditions:
            base = base.where(cond)
            count_stmt = count_stmt.where(cond)

        result = await self.session.execute(
            base.order_by(BidRecommendation.id).limit(limit).offset(offset)
        )
        total = int((await self.session.execute(count_stmt)).scalar_one())
        return list(result.scalars().all()), total


class RuleResultRepository(BaseRepository):
    """Bulk persistence for rule results."""

    async def bulk_add(self, results: Sequence[RuleResult]) -> None:
        if not results:
            return
        self.session.add_all(list(results))
        await self.session.flush()
