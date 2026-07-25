"""Route performance metrics fed into the rule engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteMetrics:
    """Historical performance for a route, sourced from route summaries.

    Any field may be ``None`` when the underlying data is unavailable; rules
    treat missing metrics as "no signal" rather than failing.
    """

    ctr: float | None = None
    avg_position: float | None = None
    spend: float | None = None
    clicks: int | None = None
    impressions: int | None = None
    bookings: int | None = None

    def get(self, key: str) -> float | None:
        """Return a metric value by rule key (as float), or ``None``."""
        value = getattr(self, key, None)
        return None if value is None else float(value)
