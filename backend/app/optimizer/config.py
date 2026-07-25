"""Configuration for the deterministic recommendation engine.

All thresholds, bid limits, CTR bands, increase percentages, and confidence
cut-offs live here — the engine logic contains no magic numbers. The default
values encode the approved KAYAK bidding strategy (Phase 3C). Adjusting the
strategy later means editing this configuration, not the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.enums import DeviceType


@dataclass(frozen=True)
class DeviceBidLimits:
    """Absolute min/max bid for a device. Bids are never recommended outside."""

    minimum: float
    maximum: float


@dataclass(frozen=True)
class CtrBands:
    """Lower CTR bounds (as fractions) for each performance class."""

    excellent: float = 0.08  # CTR >= 8%
    good: float = 0.05  # CTR >= 5%
    average: float = 0.03  # CTR >= 3%
    poor: float = 0.015  # CTR >= 1.5%  (below this = Very Poor)


@dataclass(frozen=True)
class IncreasePercents:
    """Bid-increase percentage for each CTR class (Very Poor never increases)."""

    excellent: float = 0.10
    good: float = 0.08
    average: float = 0.05
    poor: float = 0.03


@dataclass(frozen=True)
class DataThresholds:
    """Minimum data volume required before any bid is recommended."""

    min_impressions: int = 100
    min_clicks: int = 20


@dataclass(frozen=True)
class ConfidenceThresholds:
    """Data volumes defining HIGH / MEDIUM confidence (else LOW)."""

    high_impressions: int = 1000
    high_clicks: int = 100
    medium_impressions: int = 500
    medium_clicks: int = 50


@dataclass(frozen=True)
class RecommendationConfig:
    """The complete, deterministic recommendation configuration."""

    version: str = "kayak-position1-v1"
    desktop: DeviceBidLimits = field(default_factory=lambda: DeviceBidLimits(1.50, 2.20))
    mobile: DeviceBidLimits = field(default_factory=lambda: DeviceBidLimits(0.90, 2.20))
    ctr_bands: CtrBands = field(default_factory=CtrBands)
    increase: IncreasePercents = field(default_factory=IncreasePercents)
    data: DataThresholds = field(default_factory=DataThresholds)
    confidence: ConfidenceThresholds = field(default_factory=ConfidenceThresholds)
    # Consecutive prior runs at position > 1 that trigger MANUAL_REVIEW.
    consecutive_failed_runs: int = 3

    def limits_for(self, device: DeviceType) -> DeviceBidLimits:
        """Return the bid limits for a device (mobile vs desktop)."""
        return self.mobile if device is DeviceType.MOBILE else self.desktop


#: The active strategy configuration (the approved KAYAK strategy).
DEFAULT_CONFIG = RecommendationConfig()
