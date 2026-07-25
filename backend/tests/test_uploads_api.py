"""Integration tests for the upload API and import pipeline (real structure)."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tests import samples

from app.models.performance_report import PerformanceReport
from app.models.route_summary import RouteSummary

_URL = "/api/v1/uploads"
_TSV = "text/tab-separated-values"
_INLINE = "inline_7003593_flight_20260723.tsv"
_DYNAMIC = "dynamic-inline_7003593_flight_20260723.tsv"


async def test_upload_real_inline_imports_with_zero_errors(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.post(_URL, files={"file": (_INLINE, samples.inline_tsv_bytes(), _TSV)})

    assert response.status_code == 201
    body = response.json()
    assert body["upload_status"] == "completed"
    assert body["report_type"] == "inline"
    assert body["imported_rows"] == 2
    assert body["skipped_rows"] == 1  # blank row only
    assert body["error_count"] == 0
    assert body["validation_errors"] == []

    reports = await db_session.scalar(select(func.count()).select_from(PerformanceReport))
    assert reports == 2
    # Not device-segmented -> device 'all'.
    devices = await db_session.scalars(select(PerformanceReport.device).distinct())
    assert set(devices) == {"all"}
    # Bookings unavailable -> stored as NULL.
    bookings = await db_session.scalars(select(PerformanceReport.bookings))
    assert all(b is None for b in bookings)
    summaries = await db_session.scalar(select(func.count()).select_from(RouteSummary))
    assert summaries == 2


async def test_upload_real_dynamic_inline(client: AsyncClient) -> None:
    response = await client.post(
        _URL, files={"file": (_DYNAMIC, samples.dynamic_tsv_bytes(), _TSV)}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["report_type"] == "dynamic_inline"
    assert body["imported_rows"] == 2
    assert body["error_count"] == 0


async def test_legacy_report_still_imports(client: AsyncClient) -> None:
    response = await client.post(
        _URL, files={"file": ("legacy_desktop.csv", samples.legacy_csv_bytes(), "text/csv")}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["upload_status"] == "completed"
    assert body["imported_rows"] == 2
    assert body["error_count"] == 0


async def test_duplicate_upload_rejected(client: AsyncClient) -> None:
    first = await client.post(_URL, files={"file": (_INLINE, samples.inline_tsv_bytes(), _TSV)})
    assert first.status_code == 201
    second = await client.post(_URL, files={"file": (_INLINE, samples.inline_tsv_bytes(), _TSV)})
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"


async def test_unsupported_extension_rejected(client: AsyncClient) -> None:
    response = await client.post(_URL, files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 415


async def test_missing_columns_marks_failed(client: AsyncClient) -> None:
    bad = b"Origin\tEst. Clicks\nJFK\t10\n"
    response = await client.post(_URL, files={"file": ("bad.tsv", bad, _TSV)})

    assert response.status_code == 201
    body = response.json()
    assert body["upload_status"] == "failed"
    assert body["imported_rows"] == 0
    assert any(e["field"] == "columns" for e in body["validation_errors"])


async def test_list_get_delete(client: AsyncClient, db_session: AsyncSession) -> None:
    created = await client.post(_URL, files={"file": (_INLINE, samples.inline_tsv_bytes(), _TSV)})
    upload_id = created.json()["id"]

    listing = await client.get(_URL)
    assert listing.json()["total"] == 1

    detail = await client.get(f"{_URL}/{upload_id}")
    assert detail.json()["id"] == upload_id

    deleted = await client.delete(f"{_URL}/{upload_id}")
    assert deleted.status_code == 204

    summaries = await db_session.scalar(select(func.count()).select_from(RouteSummary))
    assert summaries == 0

    missing = await client.get(f"{_URL}/{upload_id}")
    assert missing.status_code == 404
