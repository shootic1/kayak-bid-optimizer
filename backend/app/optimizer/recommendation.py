"""Deterministic, explainable bid recommendation engine.

Implements the approved KAYAK strategy: always drive toward Position #1 while
respecting device bid limits, never automatically reducing a bid. The same input
always produces the same output — no randomization, no heuristics beyond the
configured rules. Every recommendation states the exact rule that produced it.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import ConfidenceLevel, DeviceType, RecommendationAction
from app.optimizer import rules
from app.optimizer.config import DEFAULT_CONFIG, RecommendationConfig
from app.optimizer.metrics import RouteMetrics
from app.optimizer.rules import CtrClass, RuleTrigger


@dataclass(frozen=True)
class Recommendation:
    """A complete, self-contained recommendation for one route."""

    action: RecommendationAction
    device: DeviceType
    current_bid: float | None
    recommended_bid: float | None
    difference: float | None
    pct_change: float | None
    current_position: float | None
    ctr: float | None
    clicks: int | None
    impressions: int | None
    spend: float | None
    reason: str
    rule_triggered: str
    confidence: ConfidenceLevel
    manual_review: bool


class RecommendationEngine:
    """Applies the deterministic strategy to a single route."""

    def __init__(self, config: RecommendationConfig = DEFAULT_CONFIG) -> None:
        self._config = config

    @property
    def config_version(self) -> str:
        return self._config.version

    def recommend(
        self,
        *,
        device: DeviceType,
        current_bid: float | None,
        metrics: RouteMetrics,
        prior_failed_runs: int = 0,
    ) -> Recommendation:
        config = self._config
        limits = config.limits_for(device)
        impressions = metrics.impressions
        clicks = metrics.clicks
        ctr = metrics.ctr
        position = metrics.avg_position
        confidence = rules.confidence_for(
            int(impressions or 0), int(clicks or 0), config.confidence
        )

        def result(
            action: RecommendationAction,
            recommended: float | None,
            trigger: RuleTrigger,
            reason: str,
            *,
            manual_review: bool = False,
        ) -> Recommendation:
            difference: float | None = None
            pct_change: float | None = None
            if current_bid is not None and recommended is not None:
                difference = round(recommended - current_bid, 4)
                pct_change = round(difference / current_bid, 6) if current_bid else None
            return Recommendation(
                action=action,
                device=device,
                current_bid=current_bid,
                recommended_bid=recommended,
                difference=difference,
                pct_change=pct_change,
                current_position=position,
                ctr=ctr,
                clicks=metrics.clicks,
                impressions=metrics.impressions,
                spend=metrics.spend,
                reason=reason,
                rule_triggered=trigger.value,
                confidence=confidence,
                manual_review=manual_review,
            )

        # 1. Missing core data required to validate.
        if impressions is None or clicks is None:
            return result(
                RecommendationAction.MANUAL_REVIEW,
                current_bid,
                RuleTrigger.MISSING_METRICS,
                "Missing or invalid metrics.",
                manual_review=True,
            )

        # 2. Data validation gates (informational spend never gates).
        if impressions < config.data.min_impressions:
            return result(
                RecommendationAction.INSUFFICIENT_DATA,
                current_bid,
                RuleTrigger.INSUFFICIENT_IMPRESSIONS,
                f"Insufficient impressions ({impressions} < {config.data.min_impressions}).",
            )
        if clicks < config.data.min_clicks:
            return result(
                RecommendationAction.INSUFFICIENT_DATA,
                current_bid,
                RuleTrigger.INSUFFICIENT_CLICKS,
                f"Insufficient clicks ({clicks} < {config.data.min_clicks}).",
            )

        # 3. Metrics required to optimize.
        if ctr is None or position is None:
            return result(
                RecommendationAction.MANUAL_REVIEW,
                current_bid,
                RuleTrigger.MISSING_METRICS,
                "Missing or invalid metrics.",
                manual_review=True,
            )

        # 4. Already at Position #1 → keep.
        if position == 1.0:
            return result(
                RecommendationAction.KEEP,
                current_bid,
                RuleTrigger.ALREADY_POSITION_1,
                "Already Position #1.",
            )

        # Position > 1 from here.
        # 5. At device maximum bid → manual review (cannot increase further).
        if current_bid is not None and current_bid >= limits.maximum:
            return result(
                RecommendationAction.MANUAL_REVIEW,
                current_bid,
                RuleTrigger.MAXIMUM_BID_REACHED,
                f"Maximum bid reached ({limits.maximum:.2f}).",
                manual_review=True,
            )

        # 6. Repeatedly failed to reach Position #1 → manual review.
        if prior_failed_runs >= config.consecutive_failed_runs:
            return result(
                RecommendationAction.MANUAL_REVIEW,
                current_bid,
                RuleTrigger.FAILED_THREE_RUNS,
                f"Failed to reach Position #1 after {prior_failed_runs} runs.",
                manual_review=True,
            )

        # 7. CTR classification.
        ctr_class = rules.classify_ctr(ctr, config.ctr_bands)
        if ctr_class is CtrClass.VERY_POOR:
            return result(
                RecommendationAction.MANUAL_REVIEW,
                current_bid,
                RuleTrigger.VERY_POOR_CTR,
                f"Very Poor CTR ({ctr * 100:.2f}%); manual review.",
                manual_review=True,
            )

        # 8. Increase by the configured percentage, clamped to device limits.
        increase_pct = rules.increase_pct_for(ctr_class, config.increase)
        recommended = current_bid
        if current_bid is not None:
            recommended = round(
                rules.clamp_to_limits(current_bid * (1.0 + increase_pct), limits), 2
            )
        return result(
            RecommendationAction.INCREASE,
            recommended,
            rules.increase_trigger_for(ctr_class),
            f"Position {position} with {ctr_class.value} CTR "
            f"({ctr * 100:.2f}%): +{round(increase_pct * 100)}%.",
        )
