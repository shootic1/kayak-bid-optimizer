"""KAYAK report detection and column validation.

Maps a report's actual headers onto canonical fields, detects the report variant
(Inline vs Dynamic Inline) and device segment, derives the report date from the
filename, and validates that the genuinely-required columns are present.

The alias map reflects the **real** KAYAK flight report structure:

Inline report columns:
    Placement, Origin, Destination, Advertiser Origin, Advertiser Destination,
    Average CPC (USD), Average Rank, First/Second/Third Rank Bid (USD) N% Share,
    Est. Clicks, Est. Impressions, Est. Spend (USD)

Dynamic Inline report columns:
    Placement, Origin, Destination, Advertiser Origin, Advertiser Destination,
    Average CPC (USD), Average Inline Ad Rank, Average Overall Position,
    Nth Overall Position Bid (USD), Bid To Be First Inline Ad,
    Est. Clicks, Est. Impressions, Est. Spend (USD)

Real reports have no Date, Device, or Bookings columns: the date comes from the
filename, device defaults to ``ALL``, and bookings is stored as ``NULL``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.enums import DeviceType, ReportType

# Canonical field -> accepted header aliases (matched case/punctuation-insensitively).
# The first alias that matches wins, so preferred headers are listed first.
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "origin": ("origin",),
    "destination": ("destination",),
    # "Est. Clicks" -> normalized "est clicks"; legacy aliases retained.
    "clicks": ("est clicks", "clicks", "click"),
    "impressions": ("est impressions", "impressions", "impr", "imps"),
    "spend": ("est spend usd", "est spend", "spend", "cost", "total spend"),
    "avg_cpc": ("average cpc usd", "average cpc", "avg cpc", "cpc"),
    # Dynamic reports expose "Average Overall Position" (preferred); inline uses
    # "Average Rank".
    "avg_position": (
        "average overall position",
        "average rank",
        "average inline ad rank",
        "average position",
        "avg position",
        "position",
        "avg pos",
    ),
    # Optional in real reports (absent -> NULL / derived).
    "ctr": ("ctr", "click through rate"),
    "bookings": ("bookings", "conversions", "conv", "booking"),
    "device": ("device", "device type", "platform"),
    "report_date": ("date", "report date", "day"),
}

# Only columns present in every real KAYAK report are enforced. Date comes from
# the filename, device defaults to ALL, bookings/ctr are optional.
REQUIRED_FIELDS: tuple[str, ...] = (
    "origin",
    "destination",
    "impressions",
    "clicks",
    "spend",
)

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_DATE_IN_NAME_RE = re.compile(r"\d{8}")


def _normalize_header(header: str) -> str:
    """Lowercase and collapse punctuation/whitespace for tolerant matching."""
    return _NORMALIZE_RE.sub(" ", header.lower()).strip()


@dataclass(frozen=True)
class DetectionResult:
    """Outcome of detecting and validating a report's structure."""

    report_type: ReportType
    report_device: DeviceType
    report_date: date | None = None
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
    """Real flight reports are not device-segmented -> ALL. Filename hints win."""
    name = filename.lower()
    if any(token in name for token in ("mobile", "phone")):
        return DeviceType.MOBILE
    if "desktop" in name:
        return DeviceType.DESKTOP
    return DeviceType.ALL


def _detect_report_date(filename: str) -> date | None:
    """Parse a ``YYYYMMDD`` token from the filename (e.g. ``..._20260723.tsv``)."""
    parsed: date | None = None
    for token in _DATE_IN_NAME_RE.findall(filename):
        try:
            parsed = datetime.strptime(token, "%Y%m%d").date()
        except ValueError:
            continue
    return parsed


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
        report_date=_detect_report_date(original_filename),
        column_map=column_map,
        device_column=column_map.get("device"),
        missing_columns=missing,
        errors=errors,
    )
