"""Route matcher unit tests."""

from __future__ import annotations

from app.domain.enums import MatchStatus
from app.optimizer.matching import BidRouteInput, RouteHistory, RouteMatcher, is_iata
from app.optimizer.metrics import RouteMetrics


def _index() -> dict[tuple[str, str], RouteHistory]:
    return {("JFK", "LAX"): RouteHistory(route_summary_id=1, metrics=RouteMetrics(ctr=0.05))}


def test_matched() -> None:
    outcome = RouteMatcher(_index()).match(BidRouteInput("JFK", "LAX", excluded=False))
    assert outcome.status is MatchStatus.MATCHED
    assert outcome.route_summary_id == 1
    assert outcome.metrics is not None


def test_unmatched_no_history() -> None:
    outcome = RouteMatcher(_index()).match(BidRouteInput("JFK", "SFO", excluded=False))
    assert outcome.status is MatchStatus.UNMATCHED_NO_HISTORY


def test_unmatched_non_iata() -> None:
    outcome = RouteMatcher({}).match(BidRouteInput("New York, NY", "LAX", excluded=False))
    assert outcome.status is MatchStatus.UNMATCHED_NON_IATA


def test_skipped_excluded_takes_priority() -> None:
    # Excluded is checked before IATA/history, so even a matchable route is skipped.
    outcome = RouteMatcher(_index()).match(BidRouteInput("JFK", "LAX", excluded=True))
    assert outcome.status is MatchStatus.SKIPPED_EXCLUDED


def test_match_is_case_insensitive() -> None:
    outcome = RouteMatcher(_index()).match(BidRouteInput("jfk", "lax", excluded=False))
    assert outcome.status is MatchStatus.MATCHED


def test_is_iata() -> None:
    assert is_iata("JFK") is True
    assert is_iata("jfk") is True
    assert is_iata("New York, NY") is False
    assert is_iata("JFKK") is False
    assert is_iata(None) is False
