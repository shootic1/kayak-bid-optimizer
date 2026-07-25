"""Bid-file parser unit tests."""

from __future__ import annotations

from pathlib import Path

from tests import bid_samples

from app.optimizer.bid_file_parser import BidFileParser


def test_parses_provider_and_mode_and_routes(tmp_path: Path) -> None:
    path = tmp_path / "bids.xlsx"
    path.write_bytes(bid_samples.bid_xlsx_bytes())

    parsed = BidFileParser().parse(path)

    assert parsed.provider_code == bid_samples.PROVIDER
    assert parsed.mode == "Full"
    assert len(parsed.routes) == len(bid_samples.DEFAULT_ROUTES)


def test_route_fields_and_iata_flags(tmp_path: Path) -> None:
    path = tmp_path / "bids.xlsx"
    path.write_bytes(bid_samples.bid_xlsx_bytes())
    routes = BidFileParser().parse(path).routes

    first = routes[0]
    assert first.origin == "JFK"
    assert first.destination == "LAX"
    assert first.override_cpc == 1.6
    assert first.origin_is_iata is True
    # Provider inherited from the Mode sheet even though only row 1 has it inline.
    assert first.provider_code == bid_samples.PROVIDER

    non_iata = [r for r in routes if not r.origin_is_iata]
    assert non_iata and non_iata[0].origin == "New York, NY"

    excluded = [r for r in routes if r.excluded]
    assert len(excluded) == 1
    assert excluded[0].origin == "BOS"
