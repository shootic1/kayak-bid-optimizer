"""Integration tests for the Excel export endpoints.

Drives the full path: seed history -> upload bid file -> run optimization ->
export. Verifies that each recommendation action maps to the correct workbook
outcome and that the export summary is accurate.
"""

from __future__ import annotations

from io import BytesIO

from httpx import AsyncClient
from openpyxl import load_workbook
from sqlalchemy.ext.asyncio import AsyncSession
from tests import bid_samples

from app.domain.enums import DeviceType
from app.models.route_summary import RouteSummary

_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_BID_URL = "/api/v1/bid-files"
_RUN_URL = "/api/v1/optimization/run"

# Mobile provider (limits 0.90-2.20). Routes chosen to hit every action:
#   JFK-LAX -> INCREASE, JFK-SFO -> KEEP (already #1),
#   MIA-JFK -> MANUAL_REVIEW (at max bid), ABE-AUA -> INSUFFICIENT_DATA (no history).
_ROUTES = [
    ("JFK", "LAX", "false", "1.60"),
    ("JFK", "SFO", "false", "1.40"),
    ("MIA", "JFK", "false", "2.20"),
    ("ABE", "AUA", "false", "1.50"),
]


def _summary(origin: str, destination: str, **kw: object) -> RouteSummary:
    values: dict[str, object] = {
        "origin": origin,
        "destination": destination,
        "device": DeviceType.ALL,
        "total_reports": 1,
        "total_impressions": 1000,
        "total_clicks": 50,
        "average_ctr": 0.05,  # Good CTR -> +8%
        "average_cpc": 1.2,
        "average_position": 1.5,
        "total_spend": 60.0,
        "total_bookings": 3,
    }
    values.update(kw)
    return RouteSummary(**values)


async def _run(client: AsyncClient, db_session: AsyncSession) -> int:
    db_session.add_all(
        [
            _summary("JFK", "LAX"),  # position 1.5 -> INCREASE
            _summary("JFK", "SFO", average_position=1.0),  # already #1 -> KEEP
            _summary("MIA", "JFK", average_position=2.0),  # at max bid -> MANUAL_REVIEW
        ]
    )
    await db_session.commit()
    upload = await client.post(
        _BID_URL,
        files={
            "file": (
                "CheapTicketsDealM_FIOAD_US.xlsx",
                bid_samples.bid_xlsx_bytes(routes=_ROUTES),
                _XLSX,
            )
        },
    )
    assert upload.status_code == 201, upload.text
    run = await client.post(_RUN_URL, json={"bid_file_id": upload.json()["id"]})
    assert run.status_code == 201, run.text
    return int(run.json()["id"])


async def test_export_summary_counts(client: AsyncClient, db_session: AsyncSession) -> None:
    run_id = await _run(client, db_session)

    resp = await client.get(f"/api/v1/optimization/runs/{run_id}/export/summary")
    assert resp.status_code == 200
    body = resp.json()

    assert body["output_filename"] == "CheapTicketsDealM_FIOAD_US_Optimized.xlsx"
    assert body["routes_processed"] == 4
    assert body["routes_updated"] == 1  # only JFK-LAX (INCREASE)
    assert body["routes_unchanged"] == 3  # KEEP + MANUAL_REVIEW + INSUFFICIENT_DATA
    assert body["manual_review_count"] == 1  # MIA-JFK
    assert body["insufficient_data_count"] == 1  # ABE-AUA
    assert body["average_bid_increase"] == 0.13  # 1.73 - 1.60
    assert body["maximum_bid_increase"] == 0.13
    assert body["skipped_routes"] == []
    assert body["strategy_version"] == "kayak-position1-v1"
    assert body["timestamp"]


async def test_export_downloads_optimized_workbook(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    run_id = await _run(client, db_session)

    resp = await client.get(f"/api/v1/optimization/runs/{run_id}/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == _XLSX
    assert (
        resp.headers["content-disposition"]
        == 'attachment; filename="CheapTicketsDealM_FIOAD_US_Optimized.xlsx"'
    )

    sheet = load_workbook(BytesIO(resp.content))["Search Terms"]
    # Rows follow the upload order (header on row 1).
    assert float(sheet["E2"].value) == 1.73  # JFK-LAX INCREASE -> written
    assert sheet["E3"].value == "1.40"  # JFK-SFO KEEP -> untouched (original string)
    assert sheet["E4"].value == "2.20"  # MIA-JFK MANUAL_REVIEW -> untouched
    assert sheet["E5"].value == "1.50"  # ABE-AUA INSUFFICIENT_DATA -> untouched


async def test_export_is_deterministic(client: AsyncClient, db_session: AsyncSession) -> None:
    run_id = await _run(client, db_session)
    first = await client.get(f"/api/v1/optimization/runs/{run_id}/export/summary")
    second = await client.get(f"/api/v1/optimization/runs/{run_id}/export/summary")
    a, b = first.json(), second.json()
    # Everything but the wall-clock timestamp is identical run to run.
    a.pop("timestamp")
    b.pop("timestamp")
    assert a == b


async def test_export_unknown_run_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/optimization/runs/999999/export")
    assert resp.status_code == 404
    summary = await client.get("/api/v1/optimization/runs/999999/export/summary")
    assert summary.status_code == 404
