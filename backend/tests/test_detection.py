"""KAYAK report detection and column-validation tests (real structure)."""

from __future__ import annotations

from datetime import date

from tests import samples

from app.domain.enums import DeviceType, ReportType
from app.importers.detection import detect_report

_INLINE_NAME = "inline_7003593_flight_20260723.tsv"
_DYNAMIC_NAME = "dynamic-inline_7003593_flight_20260723.tsv"


def test_detects_inline_report_and_maps_real_columns() -> None:
    result = detect_report(samples.INLINE_HEADERS, _INLINE_NAME)

    assert result.is_valid
    assert result.report_type is ReportType.INLINE
    assert result.column_map["origin"] == "Origin"
    assert result.column_map["clicks"] == "Est. Clicks"
    assert result.column_map["impressions"] == "Est. Impressions"
    assert result.column_map["spend"] == "Est. Spend (USD)"
    assert result.column_map["avg_cpc"] == "Average CPC (USD)"
    assert result.column_map["avg_position"] == "Average Rank"
    # No device or bookings columns in real reports.
    assert result.device_column is None
    assert "bookings" not in result.column_map
    assert result.report_device is DeviceType.ALL
    assert result.report_date == date(2026, 7, 23)


def test_detects_dynamic_inline_and_prefers_overall_position() -> None:
    result = detect_report(samples.DYNAMIC_HEADERS, _DYNAMIC_NAME)

    assert result.is_valid
    assert result.report_type is ReportType.DYNAMIC_INLINE
    assert result.column_map["avg_position"] == "Average Overall Position"
    assert result.report_date == date(2026, 7, 23)


def test_missing_required_columns_produces_detailed_errors() -> None:
    result = detect_report(["Origin", "Est. Clicks"], "partial.tsv")

    assert not result.is_valid
    assert "destination" in result.missing_columns
    assert "impressions" in result.missing_columns
    assert "spend" in result.missing_columns
    assert any("missing required column" in e for e in result.errors)


def test_advertiser_origin_does_not_collide_with_origin() -> None:
    result = detect_report(samples.INLINE_HEADERS, _INLINE_NAME)
    assert result.column_map["origin"] == "Origin"  # not "Advertiser Origin"


def test_legacy_report_still_detected() -> None:
    result = detect_report(samples.LEGACY_HEADERS, "legacy_desktop.csv")

    assert result.is_valid
    assert result.device_column == "Device"
    assert result.column_map["report_date"] == "Date"
    assert result.column_map["bookings"] == "Bookings"
