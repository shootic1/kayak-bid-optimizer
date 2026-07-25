"""Pure value-normalization functions for imported report cells.

Each function accepts a raw cell value (string, number, date, or ``None``) and
returns a clean, typed value, raising :class:`ValueError` with a human-readable
message on invalid input. Callers add row/field context to the error.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from app.domain.enums import DeviceType

_AIRPORT_RE = re.compile(r"^[A-Z]{3}$")
_CURRENCY_STRIP_RE = re.compile(r"[^\d.\-]")
_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%m-%d-%Y",
    "%d-%b-%Y",
    "%b %d, %Y",
    "%Y-%m-%d %H:%M:%S",
)

# Checked in order: mobile tokens take priority over desktop tokens so labels
# like "Mobile Web" resolve to mobile rather than matching "web" (desktop).
_MOBILE_TOKENS = ("mobile", "smartphone", "phone", "cell", "mob")
_DESKTOP_TOKENS = ("desktop", "computer", "web", "pc", "dsk")


def _as_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def normalize_airport_code(value: object) -> str:
    """Return a 3-letter uppercase IATA airport code, or raise."""
    text = _as_text(value).upper()
    if not _AIRPORT_RE.match(text):
        raise ValueError(f"invalid airport code {text!r} (expected 3 letters)")
    return text


def normalize_date(value: object) -> date:
    """Parse a date from a date/datetime object or a supported string format."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _as_text(value)
    if not text:
        raise ValueError("missing date")
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognized date format {text!r}")


def normalize_int(value: object) -> int:
    """Parse an integer, tolerating thousands separators and trailing decimals."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a valid integer")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return round(value)
    text = _as_text(value).replace(",", "").replace(" ", "")
    if not text:
        raise ValueError("missing integer value")
    try:
        return round(float(text))
    except ValueError as exc:
        raise ValueError(f"invalid integer {text!r}") from exc


def normalize_float(value: object) -> float:
    """Parse a float, tolerating thousands separators."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a valid number")
    if isinstance(value, (int, float)):
        return float(value)
    text = _as_text(value).replace(",", "").replace(" ", "")
    if not text:
        raise ValueError("missing numeric value")
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"invalid number {text!r}") from exc


def normalize_percentage(value: object) -> float:
    """Parse a percentage into a fraction. ``"2.34%"`` and ``2.34`` -> ``0.0234``."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) / 100.0
    text = _as_text(value).replace("%", "").replace(",", "").strip()
    if not text:
        raise ValueError("missing percentage value")
    try:
        return float(text) / 100.0
    except ValueError as exc:
        raise ValueError(f"invalid percentage {value!r}") from exc


def normalize_currency(value: object) -> float:
    """Parse a monetary amount, stripping currency symbols and separators."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = _as_text(value)
    if not text:
        raise ValueError("missing currency value")
    cleaned = _CURRENCY_STRIP_RE.sub("", text)
    if cleaned in ("", "-", "."):
        raise ValueError(f"invalid currency {value!r}")
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"invalid currency {value!r}") from exc


def normalize_device(value: object) -> DeviceType:
    """Map a raw device label to a :class:`DeviceType`.

    Mobile indicators are checked first so compound labels such as "Mobile Web"
    resolve to mobile.
    """
    text = _as_text(value).lower()
    if not text:
        raise ValueError("missing device")
    if any(token in text for token in _MOBILE_TOKENS):
        return DeviceType.MOBILE
    if any(token in text for token in _DESKTOP_TOKENS):
        return DeviceType.DESKTOP
    raise ValueError(f"unrecognized device {value!r}")
