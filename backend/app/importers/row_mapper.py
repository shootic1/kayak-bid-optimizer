"""Map a raw parsed row onto a normalized, validated report row.

Applies the normalization functions, derives missing metrics (CTR, avg CPC) when
possible, and rejects rows whose required fields are invalid. Blank rows are
detected so callers can skip them without recording an error.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.enums import DeviceType, ReportType
from app.importers.detection import DetectionResult
from app.importers.normalizers import (
    normalize_airport_code,
    normalize_currency,
    normalize_date,
    normalize_device,
    normalize_float,
    normalize_int,
    normalize_percentage,
)


@dataclass(frozen=True)
class RowError:
    """A single row-level validation failure."""

    row: int
    field: str
    message: str

    def as_dict(self) -> dict[str, object]:
        return {"row": self.row, "field": self.field, "message": self.message}


@dataclass(frozen=True)
class NormalizedRow:
    """A validated, normalized performance row ready for persistence."""

    report_type: ReportType
    report_date: date
    origin: str
    destination: str
    device: DeviceType
    impressions: int
    clicks: int
    ctr: float | None
    avg_cpc: float | None
    spend: float
    bookings: int
    avg_position: float | None


class RowMappingError(Exception):
    """Raised when a required field of a row fails validation."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def _raw(row: dict[str, object], column_map: dict[str, str], field_name: str) -> object:
    header = column_map.get(field_name)
    return None if header is None else row.get(header)


def _is_empty(value: object) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def is_blank_row(row: dict[str, object], detection: DetectionResult) -> bool:
    """Return True when every mapped column in the row is empty."""
    return all(_is_empty(_raw(row, detection.column_map, f)) for f in detection.column_map)


def map_row(row: dict[str, object], detection: DetectionResult) -> NormalizedRow:
    """Normalize a raw row into a :class:`NormalizedRow`.

    Raises :class:`RowMappingError` if a required field is missing/invalid.
    Optional metrics that are absent are derived when possible, else ``None``.
    """
    column_map = detection.column_map

    def required(field_name: str, normalize: object) -> object:
        value = _raw(row, column_map, field_name)
        try:
            return normalize(value)  # type: ignore[operator]
        except ValueError as exc:
            raise RowMappingError(field_name, str(exc)) from exc

    origin = required("origin", normalize_airport_code)
    destination = required("destination", normalize_airport_code)
    report_date = required("report_date", normalize_date)
    impressions = required("impressions", normalize_int)
    clicks = required("clicks", normalize_int)
    spend = required("spend", normalize_currency)
    bookings = required("bookings", normalize_int)

    # Device: from the per-row column when present/valid, else the report default.
    device = detection.report_device
    if detection.device_column is not None:
        raw_device = row.get(detection.device_column)
        if not _is_empty(raw_device):
            try:
                device = normalize_device(raw_device)
            except ValueError:
                device = detection.report_device

    # Optional metrics: use the column when present, else derive.
    ctr = _optional_or_derive(
        row, column_map, "ctr", normalize_percentage, _safe_ratio(clicks, impressions)
    )
    avg_cpc = _optional_or_derive(
        row, column_map, "avg_cpc", normalize_currency, _safe_ratio(spend, clicks)
    )
    avg_position = _optional_or_derive(row, column_map, "avg_position", normalize_float, None)

    return NormalizedRow(
        report_type=detection.report_type,
        report_date=report_date,  # type: ignore[arg-type]
        origin=origin,  # type: ignore[arg-type]
        destination=destination,  # type: ignore[arg-type]
        device=device,
        impressions=impressions,  # type: ignore[arg-type]
        clicks=clicks,  # type: ignore[arg-type]
        ctr=ctr,
        avg_cpc=avg_cpc,
        spend=spend,  # type: ignore[arg-type]
        bookings=bookings,  # type: ignore[arg-type]
        avg_position=avg_position,
    )


def _safe_ratio(numerator: object, denominator: object) -> float | None:
    if isinstance(numerator, (int, float)) and isinstance(denominator, (int, float)):
        return float(numerator) / float(denominator) if denominator else None
    return None


def _optional_or_derive(
    row: dict[str, object],
    column_map: dict[str, str],
    field_name: str,
    normalize: object,
    derived: float | None,
) -> float | None:
    """Return a normalized optional metric, or the derived fallback."""
    header = column_map.get(field_name)
    if header is not None:
        value = row.get(header)
        if not _is_empty(value):
            try:
                return float(normalize(value))  # type: ignore[operator]
            except ValueError:
                return derived
    return derived
