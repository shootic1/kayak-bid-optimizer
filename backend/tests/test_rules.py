"""Unit tests for the deterministic rule helpers."""

from __future__ import annotations

import pytest

from app.domain.enums import ConfidenceLevel, DeviceType
from app.optimizer.config import DEFAULT_CONFIG, DeviceBidLimits
from app.optimizer.rules import (
    CtrClass,
    RuleTrigger,
    clamp_to_limits,
    classify_ctr,
    confidence_for,
    device_for_provider,
    increase_pct_for,
    increase_trigger_for,
)

_C = DEFAULT_CONFIG


@pytest.mark.parametrize(
    ("ctr", "expected"),
    [
        (0.10, CtrClass.EXCELLENT),
        (0.08, CtrClass.EXCELLENT),
        (0.079, CtrClass.GOOD),
        (0.05, CtrClass.GOOD),
        (0.049, CtrClass.AVERAGE),
        (0.03, CtrClass.AVERAGE),
        (0.029, CtrClass.POOR),
        (0.015, CtrClass.POOR),
        (0.0149, CtrClass.VERY_POOR),
        (0.0, CtrClass.VERY_POOR),
    ],
)
def test_classify_ctr(ctr: float, expected: CtrClass) -> None:
    assert classify_ctr(ctr, _C.ctr_bands) is expected


def test_increase_pct_for() -> None:
    assert increase_pct_for(CtrClass.EXCELLENT, _C.increase) == 0.10
    assert increase_pct_for(CtrClass.GOOD, _C.increase) == 0.08
    assert increase_pct_for(CtrClass.AVERAGE, _C.increase) == 0.05
    assert increase_pct_for(CtrClass.POOR, _C.increase) == 0.03


def test_increase_trigger_for() -> None:
    assert increase_trigger_for(CtrClass.EXCELLENT) is RuleTrigger.EXCELLENT_CTR_INCREASE
    assert increase_trigger_for(CtrClass.GOOD) is RuleTrigger.GOOD_CTR_INCREASE
    assert increase_trigger_for(CtrClass.AVERAGE) is RuleTrigger.AVERAGE_CTR_INCREASE
    assert increase_trigger_for(CtrClass.POOR) is RuleTrigger.POOR_CTR_INCREASE


@pytest.mark.parametrize(
    ("impressions", "clicks", "expected"),
    [
        (1000, 100, ConfidenceLevel.HIGH),
        (5000, 500, ConfidenceLevel.HIGH),
        (1000, 99, ConfidenceLevel.MEDIUM),  # clicks below HIGH but meets MEDIUM
        (500, 50, ConfidenceLevel.MEDIUM),
        (499, 50, ConfidenceLevel.LOW),
        (500, 49, ConfidenceLevel.LOW),
        (100, 20, ConfidenceLevel.LOW),
    ],
)
def test_confidence_for(impressions: int, clicks: int, expected: ConfidenceLevel) -> None:
    assert confidence_for(impressions, clicks, _C.confidence) is expected


def test_device_for_provider() -> None:
    assert device_for_provider("CheapTicketsDealM_FIOAD_US") is DeviceType.MOBILE
    assert device_for_provider("CheapTicketsDealD_FIOAD_US") is DeviceType.DESKTOP
    assert device_for_provider("SomethingElse") is DeviceType.DESKTOP  # conservative default


def test_clamp_to_limits() -> None:
    limits = DeviceBidLimits(1.50, 2.20)
    assert clamp_to_limits(1.40, limits) == 1.50
    assert clamp_to_limits(2.50, limits) == 2.20
    assert clamp_to_limits(1.80, limits) == 1.80
