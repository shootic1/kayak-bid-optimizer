"""Small, pure, deterministic rule functions used by the recommendation engine.

Each function is independently testable and takes its thresholds from
configuration — there are no hardcoded values here.
"""

from __future__ import annotations

from enum import StrEnum

from app.domain.enums import ConfidenceLevel, DeviceType
from app.optimizer.config import (
    ConfidenceThresholds,
    CtrBands,
    DeviceBidLimits,
    IncreasePercents,
)


class CtrClass(StrEnum):
    """CTR performance classification."""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    VERY_POOR = "very_poor"


class RuleTrigger(StrEnum):
    """The rule that generated a recommendation (stored on the output)."""

    ALREADY_POSITION_1 = "Already Position #1"
    EXCELLENT_CTR_INCREASE = "Excellent CTR Increase"
    GOOD_CTR_INCREASE = "Good CTR Increase"
    AVERAGE_CTR_INCREASE = "Average CTR Increase"
    POOR_CTR_INCREASE = "Poor CTR Increase"
    VERY_POOR_CTR = "Very Poor CTR"
    MAXIMUM_BID_REACHED = "Maximum Bid Reached"
    INSUFFICIENT_IMPRESSIONS = "Insufficient Impressions"
    INSUFFICIENT_CLICKS = "Insufficient Clicks"
    MISSING_METRICS = "Missing or Invalid Metrics"
    FAILED_THREE_RUNS = "Failed to Reach Position #1 After Three Runs"
    NO_HISTORY = "No Historical Data"
    NON_IATA_ROUTE = "Non-IATA Route"
    EXCLUDED_ROUTE = "Excluded Route"


def classify_ctr(ctr: float, bands: CtrBands) -> CtrClass:
    """Classify a click-through rate (a fraction, e.g. 0.06 = 6%)."""
    if ctr >= bands.excellent:
        return CtrClass.EXCELLENT
    if ctr >= bands.good:
        return CtrClass.GOOD
    if ctr >= bands.average:
        return CtrClass.AVERAGE
    if ctr >= bands.poor:
        return CtrClass.POOR
    return CtrClass.VERY_POOR


_INCREASE_TRIGGER: dict[CtrClass, RuleTrigger] = {
    CtrClass.EXCELLENT: RuleTrigger.EXCELLENT_CTR_INCREASE,
    CtrClass.GOOD: RuleTrigger.GOOD_CTR_INCREASE,
    CtrClass.AVERAGE: RuleTrigger.AVERAGE_CTR_INCREASE,
    CtrClass.POOR: RuleTrigger.POOR_CTR_INCREASE,
}


def increase_pct_for(ctr_class: CtrClass, increase: IncreasePercents) -> float:
    """Return the configured increase percentage for a (non-Very-Poor) CTR class."""
    return {
        CtrClass.EXCELLENT: increase.excellent,
        CtrClass.GOOD: increase.good,
        CtrClass.AVERAGE: increase.average,
        CtrClass.POOR: increase.poor,
    }[ctr_class]


def increase_trigger_for(ctr_class: CtrClass) -> RuleTrigger:
    """Return the rule trigger for an increase driven by a CTR class."""
    return _INCREASE_TRIGGER[ctr_class]


def confidence_for(
    impressions: int, clicks: int, thresholds: ConfidenceThresholds
) -> ConfidenceLevel:
    """Determine confidence from data volume."""
    if impressions >= thresholds.high_impressions and clicks >= thresholds.high_clicks:
        return ConfidenceLevel.HIGH
    if impressions >= thresholds.medium_impressions and clicks >= thresholds.medium_clicks:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def device_for_provider(provider_code: str) -> DeviceType:
    """Derive the device from a bid-file provider code.

    KAYAK provider codes encode the campaign: ``...DealD...`` = Desktop,
    ``...DealM...`` = Mobile. Unknown providers default to Desktop (the more
    conservative floor).
    """
    code = provider_code.lower()
    if "deald" in code:
        return DeviceType.DESKTOP
    if "dealm" in code:
        return DeviceType.MOBILE
    return DeviceType.DESKTOP


def clamp_to_limits(bid: float, limits: DeviceBidLimits) -> float:
    """Clamp a bid into ``[minimum, maximum]``."""
    return min(max(bid, limits.minimum), limits.maximum)
