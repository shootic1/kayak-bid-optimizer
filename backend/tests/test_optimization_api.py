"""Integration tests for bid files, optimization runs, and recommendations."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tests import bid_samples

from app.domain.enums import DeviceType
from app.models.optimization import RuleResult
from app.models.route_summary import RouteSummary

_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_BID_URL = "/api/v1/bid-files"
_RUN_URL = "/api/v1/optimization/run"


def _summary(origin: str, destination: str, **kw: object) -> RouteSummary:
    values: dict[str, object] = {
        "origin": origin,
        "destination": destination,
        "device": DeviceType.ALL,
        "total_reports": 1,
        "total_impressions": 1000,
        "total_clicks": 50,
        "average_ctr": 0.05,
        "average_cpc": 1.2,
        "average_position": 1.5,
        "total_spend": 60.0,
        "total_bookings": 3,
    }
    values.update(kw)
    return RouteSummary(**values)


async def _seed_history(db_session: AsyncSession) -> None:
    db_session.add_all([_summary("JFK", "LAX"), _summary("JFK", "SFO")])
    await db_session.commit()


async def _upload_bid(client: AsyncClient) -> int:
    response = await client.post(
        _BID_URL,
        files={
            "file": (
                "SearchTerms-CheapTicketsDealM_FIOAD_US.xlsx",
                bid_samples.bid_xlsx_bytes(),
                _XLSX,
            )
        },
    )
    assert response.status_code == 201, response.text
    return int(response.json()["id"])


async def test_bid_file_upload_parses_provider_and_routes(client: AsyncClient) -> None:
    response = await client.post(
        _BID_URL, files={"file": ("bids.xlsx", bid_samples.bid_xlsx_bytes(), _XLSX)}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["provider_code"] == bid_samples.PROVIDER
    assert body["mode"] == "Full"
    assert body["route_count"] == len(bid_samples.DEFAULT_ROUTES)


async def test_duplicate_bid_file_rejected(client: AsyncClient) -> None:
    await _upload_bid(client)
    dup = await client.post(
        _BID_URL, files={"file": ("bids.xlsx", bid_samples.bid_xlsx_bytes(), _XLSX)}
    )
    assert dup.status_code == 409


async def test_non_xlsx_bid_file_rejected(client: AsyncClient) -> None:
    response = await client.post(_BID_URL, files={"file": ("bids.csv", b"a,b\n1,2\n", "text/csv")})
    assert response.status_code == 415


async def test_run_generates_recommendations_with_all_statuses(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed_history(db_session)
    bid_file_id = await _upload_bid(client)

    run = await client.post(_RUN_URL, json={"bid_file_id": bid_file_id})
    assert run.status_code == 201
    body = run.json()
    assert body["status"] == "completed"
    assert body["ruleset_version"] == "kayak-position1-v1"
    assert body["total_routes"] == 5
    assert body["matched_count"] == 2  # JFK-LAX, JFK-SFO
    assert body["skipped_count"] == 1  # BOS-MIA excluded
    assert body["unmatched_count"] == 2  # ABE-AUA (no history) + New York (non-IATA)
    assert body["recommendation_count"] == 2

    run_id = body["id"]
    all_recs = await client.get(f"/api/v1/recommendations?run_id={run_id}")
    assert all_recs.json()["total"] == 5  # one row per route

    matched = await client.get(f"/api/v1/recommendations?run_id={run_id}&status=matched")
    assert matched.json()["total"] == 2
    non_iata = await client.get(
        f"/api/v1/recommendations?run_id={run_id}&status=unmatched_non_iata"
    )
    assert non_iata.json()["total"] == 1

    rec_id = matched.json()["items"][0]["id"]
    detail = await client.get(f"/api/v1/recommendations/{rec_id}")
    d = detail.json()
    # Seeded metrics: position 1.5, CTR 5% (Good) -> +8% increase (mobile provider).
    assert d["action"] == "increase"
    assert d["device"] == "mobile"
    assert d["rule_triggered"] == "Good CTR Increase"
    assert d["confidence_level"] == "medium"  # 1000 impressions, 50 clicks
    assert d["recommended_bid"] > d["current_bid"]
    assert d["current_position"] == 1.5
    assert d["manual_review"] is False
    assert len(d["rule_results"]) == 1  # one rule result per matched recommendation

    # One rule result per matched recommendation (2).
    rule_count = await db_session.scalar(select(func.count()).select_from(RuleResult))
    assert rule_count == 2


async def test_confidence_filter(client: AsyncClient, db_session: AsyncSession) -> None:
    await _seed_history(db_session)
    bid_file_id = await _upload_bid(client)
    run = await client.post(_RUN_URL, json={"bid_file_id": bid_file_id})
    run_id = run.json()["id"]
    # Matched routes have MEDIUM confidence (~0.66); unmatched/skipped => LOW (~0.33).
    mid = await client.get(f"/api/v1/recommendations?run_id={run_id}&min_confidence=0.5")
    assert mid.json()["total"] == 2


async def test_manual_review_for_maximum_bid(client: AsyncClient, db_session: AsyncSession) -> None:
    """A matched route already at the device maximum -> MANUAL_REVIEW."""
    # Mobile max is 2.20; seed a route at the ceiling with position > 1.
    db_session.add(_summary("MIA", "JFK", average_position=2.0))
    await db_session.commit()
    upload = await client.post(
        _BID_URL,
        files={
            "file": (
                "SearchTerms-CheapTicketsDealM_FIOAD_US.xlsx",
                bid_samples.bid_xlsx_bytes(routes=[("MIA", "JFK", "false", "2.20")]),
                _XLSX,
            )
        },
    )
    run = await client.post(_RUN_URL, json={"bid_file_id": upload.json()["id"]})
    recs = await client.get(f"/api/v1/recommendations?run_id={run.json()['id']}&status=matched")
    rec = recs.json()["items"][0]
    assert rec["action"] == "manual_review"
    assert rec["rule_triggered"] == "Maximum Bid Reached"
    assert rec["manual_review"] is True


async def test_run_unknown_bid_file_returns_404(client: AsyncClient) -> None:
    response = await client.post(_RUN_URL, json={"bid_file_id": 999999})
    assert response.status_code == 404


async def test_runs_list_and_get(client: AsyncClient, db_session: AsyncSession) -> None:
    await _seed_history(db_session)
    bid_file_id = await _upload_bid(client)
    created = await client.post(_RUN_URL, json={"bid_file_id": bid_file_id})
    run_id = created.json()["id"]

    listing = await client.get("/api/v1/optimization/runs")
    assert listing.json()["total"] == 1

    fetched = await client.get(f"/api/v1/optimization/runs/{run_id}")
    assert fetched.json()["id"] == run_id


async def test_performance_many_routes(client: AsyncClient, db_session: AsyncSession) -> None:
    # Seed 300 history rows and a bid file whose routes all match.
    codes = [f"{a}{b}{c}" for a in "ABC" for b in "ABCDE" for c in "ABCDEFGHIJKLMNOPQRST"][:300]
    db_session.add_all([_summary(code, "LAX") for code in codes])
    await db_session.commit()

    routes = [(code, "LAX", "false", "1.60") for code in codes]
    upload = await client.post(
        _BID_URL, files={"file": ("perf.xlsx", bid_samples.bid_xlsx_bytes(routes=routes), _XLSX)}
    )
    bid_file_id = upload.json()["id"]

    run = await client.post(_RUN_URL, json={"bid_file_id": bid_file_id})
    body = run.json()
    assert body["status"] == "completed"
    assert body["total_routes"] == 300
    assert body["matched_count"] == 300
