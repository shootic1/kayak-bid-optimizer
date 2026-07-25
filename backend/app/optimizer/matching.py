"""Route matching between bid-file routes and historical performance.

Deterministic and 1:1: a bid route resolves to exactly one status. History is
keyed by ``(origin, destination)`` (device is not a dimension in the real data —
all performance is un-segmented), guaranteeing no ambiguous matches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.enums import MatchStatus
from app.optimizer.metrics import RouteMetrics

_IATA_RE = re.compile(r"^[A-Z]{3}$")


def is_iata(code: str | None) -> bool:
    """True when ``code`` is a 3-letter IATA airport code."""
    return bool(code and _IATA_RE.match(code.strip().upper()))


@dataclass(frozen=True)
class BidRouteInput:
    origin: str
    destination: str
    excluded: bool


@dataclass(frozen=True)
class RouteHistory:
    route_summary_id: int
    metrics: RouteMetrics


@dataclass(frozen=True)
class MatchOutcome:
    status: MatchStatus
    route_summary_id: int | None
    metrics: RouteMetrics | None


class RouteMatcher:
    """Matches bid routes against a prebuilt ``(origin, destination)`` index."""

    def __init__(self, history_index: dict[tuple[str, str], RouteHistory]) -> None:
        self._index = history_index

    def match(self, route: BidRouteInput) -> MatchOutcome:
        if route.excluded:
            return MatchOutcome(MatchStatus.SKIPPED_EXCLUDED, None, None)

        origin = route.origin.strip().upper()
        destination = route.destination.strip().upper()
        if not (is_iata(origin) and is_iata(destination)):
            return MatchOutcome(MatchStatus.UNMATCHED_NON_IATA, None, None)

        history = self._index.get((origin, destination))
        if history is None:
            return MatchOutcome(MatchStatus.UNMATCHED_NO_HISTORY, None, None)

        return MatchOutcome(MatchStatus.MATCHED, history.route_summary_id, history.metrics)
