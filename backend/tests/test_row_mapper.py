"""Row mapping / normalization / rejection tests (real structure)."""

from __future__ import annotations

from datetime import date

import pytest
from tests import samples

from app.domain.enums import DeviceType, ReportType
from app.importers.detection import detect_report
from app.importers.row_mapper import RowMappingError, is_blank_row, map_row

_INLINE_NAME = "inline_7003593_flight_20260723.tsv"
_DYNAMIC_NAME = "dynamic-inline_7003593_flight_20260723.tsv"


def _inline_row(index: int) -> dict[str, object]:
    return dict(zip(samples.INLINE_HEADERS, samples.INLINE_ROWS[index], strict=True))


def _inline_detection():
    return detect_report(samples.INLINE_HEADERS, _INLINE_NAME)


def test_maps_real_inline_row() -> None:
    normalized = map_row(_inline_row(0), _inline_detection())

    assert normalized.origin == "JFK"
    assert normalized.destination == "LAX"
    assert normalized.report_type is ReportType.INLINE
    assert normalized.device is DeviceType.ALL  # no device column
    assert normalized.report_date == date(2026, 7, 23)  # from filename
    assert normalized.impressions == 1000
    assert normalized.clicks == 50
    assert normalized.spend == pytest.approx(60.0)
    assert normalized.avg_cpc == pytest.approx(1.40)
    assert normalized.avg_position == pytest.approx(1.0)  # Average Rank
    assert normalized.ctr == pytest.approx(50 / 1000)  # derived (no CTR column)
    assert normalized.bookings is None  # no bookings column -> NULL


def test_maps_real_dynamic_row_uses_overall_position() -> None:
    detection = detect_report(samples.DYNAMIC_HEADERS, _DYNAMIC_NAME)
    row = dict(zip(samples.DYNAMIC_HEADERS, samples.DYNAMIC_ROWS[0], strict=True))

    normalized = map_row(row, detection)

    assert normalized.report_type is ReportType.DYNAMIC_INLINE
    assert normalized.origin == "ABE"
    assert normalized.avg_position == pytest.approx(6.0)  # Average Overall Position
    assert normalized.bookings is None


def test_detects_blank_row() -> None:
    detection = _inline_detection()
    assert is_blank_row(_inline_row(2), detection) is True
    assert is_blank_row(_inline_row(0), detection) is False


def test_rejects_invalid_origin() -> None:
    detection = _inline_detection()
    row = dict(zip(samples.INLINE_HEADERS, samples.INVALID_INLINE_ROW, strict=True))
    with pytest.raises(RowMappingError) as exc:
        map_row(row, detection)
    assert exc.value.field == "origin"


def test_legacy_row_backward_compatible() -> None:
    detection = detect_report(samples.LEGACY_HEADERS, "legacy_desktop.csv")
    row = dict(zip(samples.LEGACY_HEADERS, samples.LEGACY_ROWS[0], strict=True))

    normalized = map_row(row, detection)

    assert normalized.device is DeviceType.DESKTOP  # from Device column
    assert normalized.report_date == date(2026, 7, 1)  # per-row Date column
    assert normalized.bookings == 3  # Bookings column present
    assert normalized.ctr == pytest.approx(0.05)  # 5.0%
