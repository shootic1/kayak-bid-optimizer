"""KAYAK report detection and column-validation tests."""

from __future__ import annotations

from tests import samples

from app.domain.enums import DeviceType, ReportType
from app.importers.detection import detect_report


def test_detects_valid_report_and_maps_columns() -> None:
    result = detect_report(samples.HEADERS, "kayak_inline_desktop.csv")

    assert result.is_valid
    assert result.report_type is ReportType.INLINE
    assert result.column_map["origin"] == "Origin"
    assert result.column_map["avg_cpc"] == "Avg CPC"
    assert result.device_column == "Device"


def test_detects_dynamic_inline_from_filename() -> None:
    result = detect_report(samples.HEADERS, "dynamic_inline_report.csv")
    assert result.report_type is ReportType.DYNAMIC_INLINE


def test_detects_mobile_from_filename() -> None:
    result = detect_report(samples.HEADERS, "kayak_inline_mobile.csv")
    assert result.report_device is DeviceType.MOBILE


def test_missing_required_columns_produces_detailed_errors() -> None:
    headers = ["Origin", "Clicks"]  # missing destination, impressions, spend, bookings, date
    result = detect_report(headers, "partial.csv")

    assert not result.is_valid
    assert "destination" in result.missing_columns
    assert "report_date" in result.missing_columns
    assert any("missing required column" in e for e in result.errors)


def test_alias_matching_is_case_and_punctuation_insensitive() -> None:
    headers = ["report date", "ORIGIN", "Destination", "impr", "click", "cost", "conversions"]
    result = detect_report(headers, "r.csv")
    assert result.is_valid
    assert result.column_map["impressions"] == "impr"
    assert result.column_map["spend"] == "cost"
