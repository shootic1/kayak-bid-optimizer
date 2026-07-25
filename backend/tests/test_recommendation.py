"""Unit tests for the deterministic recommendation engine (Phase 3C strategy)."""

from __future__ import annotations

import pytest

from app.domain.enums import ConfidenceLevel, DeviceType, RecommendationAction
from app.optimizer.metrics import RouteMetrics
from app.optimizer.recommendation import Recommendation, RecommendationEngine

_ENGINE = RecommendationEngine()


def _rec(
    *,
    device: DeviceType = DeviceType.DESKTOP,
    current: float | None = 1.60,
    prior_failed: int = 0,
    position: float | None = 2.0,
    ctr: float | None = 0.06,
    impressions: int | None = 1000,
    clicks: int | None = 100,
) -> Recommendation:
    return _ENGINE.recommend(
        device=device,
        current_bid=current,
        metrics=RouteMetrics(
            avg_position=position, ctr=ctr, impressions=impressions, clicks=clicks, spend=42.0
        ),
        prior_failed_runs=prior_failed,
    )


def test_position_1_keeps() -> None:
    r = _rec(current=1.80, position=1.0)
    assert r.action is RecommendationAction.KEEP
    assert r.recommended_bid == 1.80
    assert r.rule_triggered == "Already Position #1"


@pytest.mark.parametrize(
    ("ctr", "expected_bid", "trigger"),
    [
        (0.08, 1.76, "Excellent CTR Increase"),  # +10%
        (0.05, 1.73, "Good CTR Increase"),  # +8% -> 1.728
        (0.03, 1.68, "Average CTR Increase"),  # +5%
        (0.015, 1.65, "Poor CTR Increase"),  # +3% -> 1.648
    ],
)
def test_position_gt1_ctr_increases(ctr: float, expected_bid: float, trigger: str) -> None:
    r = _rec(current=1.60, position=2.0, ctr=ctr)
    assert r.action is RecommendationAction.INCREASE
    assert r.recommended_bid == pytest.approx(expected_bid)
    assert r.rule_triggered == trigger


def test_very_poor_ctr_manual_review() -> None:
    r = _rec(current=1.60, position=2.0, ctr=0.01)
    assert r.action is RecommendationAction.MANUAL_REVIEW
    assert r.manual_review is True
    assert r.rule_triggered == "Very Poor CTR"
    assert r.recommended_bid == 1.60  # bid held


def test_maximum_bid_desktop_manual_review() -> None:
    r = _rec(device=DeviceType.DESKTOP, current=2.20, position=2.0, ctr=0.08)
    assert r.action is RecommendationAction.MANUAL_REVIEW
    assert r.rule_triggered == "Maximum Bid Reached"


def test_maximum_bid_mobile_manual_review() -> None:
    r = _rec(device=DeviceType.MOBILE, current=2.20, position=2.0, ctr=0.08)
    assert r.action is RecommendationAction.MANUAL_REVIEW
    assert r.rule_triggered == "Maximum Bid Reached"


def test_desktop_minimum_bid_clamp() -> None:
    # Desktop min is 1.50; a small increase from 1.40 clamps up to the floor.
    r = _rec(device=DeviceType.DESKTOP, current=1.40, position=2.0, ctr=0.015)
    assert r.action is RecommendationAction.INCREASE
    assert r.recommended_bid == 1.50


def test_mobile_minimum_bid_clamp() -> None:
    # Mobile min is 0.90.
    r = _rec(device=DeviceType.MOBILE, current=0.80, position=2.0, ctr=0.015)
    assert r.recommended_bid == 0.90


def test_desktop_maximum_bid_clamp() -> None:
    # Increase from 2.10 by +10% -> 2.31, clamped to the 2.20 ceiling.
    r = _rec(device=DeviceType.DESKTOP, current=2.10, position=2.0, ctr=0.08)
    assert r.action is RecommendationAction.INCREASE
    assert r.recommended_bid == 2.20


def test_mobile_maximum_bid_clamp() -> None:
    r = _rec(device=DeviceType.MOBILE, current=2.10, position=2.0, ctr=0.08)
    assert r.recommended_bid == 2.20


def test_insufficient_impressions() -> None:
    r = _rec(current=1.60, position=2.0, ctr=0.06, impressions=50, clicks=100)
    assert r.action is RecommendationAction.INSUFFICIENT_DATA
    assert r.rule_triggered == "Insufficient Impressions"
    assert r.recommended_bid == 1.60


def test_insufficient_clicks() -> None:
    r = _rec(current=1.60, position=2.0, ctr=0.06, impressions=1000, clicks=10)
    assert r.action is RecommendationAction.INSUFFICIENT_DATA
    assert r.rule_triggered == "Insufficient Clicks"


def test_missing_metrics_manual_review() -> None:
    r = _rec(position=None, ctr=None, impressions=1000, clicks=100)
    assert r.action is RecommendationAction.MANUAL_REVIEW
    assert r.rule_triggered == "Missing or Invalid Metrics"


def test_failed_three_runs_manual_review() -> None:
    r = _rec(current=1.60, position=2.0, ctr=0.06, prior_failed=3)
    assert r.action is RecommendationAction.MANUAL_REVIEW
    assert r.rule_triggered == "Failed to Reach Position #1 After Three Runs"


@pytest.mark.parametrize(
    ("impressions", "clicks", "expected"),
    [
        (1000, 100, ConfidenceLevel.HIGH),
        (500, 50, ConfidenceLevel.MEDIUM),
        (200, 30, ConfidenceLevel.LOW),
    ],
)
def test_confidence_levels(impressions: int, clicks: int, expected: ConfidenceLevel) -> None:
    r = _rec(current=1.60, position=2.0, ctr=0.06, impressions=impressions, clicks=clicks)
    assert r.confidence is expected


def test_never_reduces_bid() -> None:
    # Even worst allowed (Poor) CTR only increases; no action reduces a bid.
    for ctr in (0.015, 0.03, 0.05, 0.08):
        r = _rec(current=1.60, position=2.0, ctr=ctr)
        assert r.recommended_bid is not None
        assert r.recommended_bid >= 1.60


def test_determinism() -> None:
    a = _rec(current=1.60, position=2.0, ctr=0.05, impressions=1000, clicks=100)
    b = _rec(current=1.60, position=2.0, ctr=0.05, impressions=1000, clicks=100)
    assert a == b
