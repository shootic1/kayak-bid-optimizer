"""Row mapping / normalization / rejection tests."""

from __future__ import annotations

from datetime import date

import pytest
from tests import samples

from app.domain.enums import DeviceType, ReportType
from app.importers.detection import detect_report
from app.importers.row_mapper import RowMappingError, is_blank_row, map_row


def _row(index: int) -> dict[str, object]:
    return dict(zip(samples.HEADERS, samples.ROWS[index], strict=True))


def _detection() -> object:
    return detect_report(samples.HEADERS, "kayak_inline_desktop.csv")


def test_maps_valid_row() -> None:
    detection = _detection()
    normalized = map_row(_row(0), detection)  # type: ignore[arg-type]

    assert normalized.origin == "JFK"
    assert normalized.destination == "LAX"
    assert normalized.report_date == date(2026, 7, 1)
    assert normalized.device is DeviceType.DESKTOP
    assert normalized.report_type is ReportType.INLINE
    assert normalized.impressions == 1000
    assert normalized.clicks == 50
    assert normalized.ctr == pytest.approx(0.05)
    assert normalized.avg_cpc == pytest.approx(1.20)
    assert normalized.spend == pytest.approx(60.0)
    assert normalized.bookings == 3
    assert normalized.avg_position == pytest.approx(2.1)


def test_detects_blank_row() -> None:
    detection = _detection()
    assert is_blank_row(_row(2), detection) is True
    assert is_blank_row(_row(0), detection) is False


def test_rejects_invalid_required_field() -> None:
    detection = _detection()
    with pytest.raises(RowMappingError) as exc:
        map_row(_row(3), detection)  # origin "XX" is invalid
    assert exc.value.field == "origin"


def test_derives_ctr_and_cpc_when_columns_absent() -> None:
    headers = ["Date", "Origin", "Destination", "Impressions", "Clicks", "Spend", "Bookings"]
    detection = detect_report(headers, "kayak_inline_desktop.csv")
    raw = dict(zip(headers, ["2026-07-01", "JFK", "LAX", "1000", "50", "60", "3"], strict=True))

    normalized = map_row(raw, detection)

    assert normalized.ctr == pytest.approx(50 / 1000)
    assert normalized.avg_cpc == pytest.approx(60 / 50)
    assert normalized.avg_position is None
    # No device column and no device hint in filename -> default desktop.
    assert normalized.device is DeviceType.DESKTOP
