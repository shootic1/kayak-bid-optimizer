"""KAYAK report detection and column validation.

Given the parsed headers and the original filename, detect the report variant
(Inline vs Dynamic Inline), resolve the device segment (Desktop vs Mobile), map
the report's actual headers onto canonical fields, and validate that all required
columns are present — returning detailed, actionable errors when they are not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.domain.enums import DeviceType, ReportType

# Canonical field -> accepted header aliases (matched case/punctuation-insensitively).
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "report_date": ("date", "report date", "day"),
    "origin": ("origin", "origin airport", "from", "orig", "departure"),
    "destination": ("destination", "destination airport", "to", "dest", "arrival"),
    "device": ("device", "device type", "platform"),
    "impressions": ("impressions", "impr", "imps"),
    "clicks": ("clicks", "click"),
    "ctr": ("ctr", "click through rate"),
    "avg_cpc": ("avg cpc", "average cpc", "cpc"),
    "spend": ("spend", "cost", "total spend"),
    "bookings": ("bookings", "conversions", "conv", "booking"),
    "avg_position": ("avg position", "average position", "position", "avg pos"),
}

# Fields a valid KAYAK performance report must contain.
REQUIRED_FIELDS: tuple[str, ...] = (
    "report_date",
    "origin",
    "destination",
    "impressions",
    "clicks",
    "spend",
    "bookings",
)

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def _normalize_header(header: str) -> str:
    """Lowercase and collapse punctuation/whitespace for tolerant matching."""
    return _NORMALIZE_RE.sub(" ", header.lower()).strip()


@dataclass(frozen=True)
class DetectionResult:
    """Outcome of detecting and validating a report's structure."""

    report_type: ReportType
    report_device: DeviceType
    column_map: dict[str, str] = field(default_factory=dict)
    device_column: str | None = None
    missing_columns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.missing_columns and not self.errors


def _detect_report_type(headers: list[str], filename: str) -> ReportType:
    haystack = " ".join(_normalize_header(h) for h in headers) + " " + filename.lower()
    return ReportType.DYNAMIC_INLINE if "dynamic" in haystack else ReportType.INLINE


def _detect_report_device(filename: str) -> DeviceType:
    name = filename.lower()
    if any(token in name for token in ("mobile", "mob", "phone")):
        return DeviceType.MOBILE
    return DeviceType.DESKTOP


def detect_report(headers: list[str], original_filename: str) -> DetectionResult:
    """Detect report metadata and validate required columns."""
    normalized_to_actual: dict[str, str] = {}
    for header in headers:
        norm = _normalize_header(header)
        if norm and norm not in normalized_to_actual:
            normalized_to_actual[norm] = header

    column_map: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized_to_actual:
                column_map[canonical] = normalized_to_actual[alias]
                break

    missing = [f for f in REQUIRED_FIELDS if f not in column_map]
    errors = [f"missing required column: {f}" for f in missing]

    return DetectionResult(
        report_type=_detect_report_type(headers, original_filename),
        report_device=_detect_report_device(original_filename),
        column_map=column_map,
        device_column=column_map.get("device"),
        missing_columns=missing,
        errors=errors,
    )
