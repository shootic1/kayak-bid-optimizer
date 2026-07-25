"""Integration tests for the upload API and import pipeline."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tests import samples

from app.models.performance_report import PerformanceReport
from app.models.route_summary import RouteSummary

_URL = "/api/v1/uploads"


async def test_upload_csv_imports_and_summarizes(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.post(
        _URL, files={"file": ("kayak_inline_desktop.csv", samples.csv_bytes(), "text/csv")}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["upload_status"] == "completed"
    assert body["report_type"] == "inline"
    assert body["imported_rows"] == 2
    assert body["skipped_rows"] == 2  # one blank row + one invalid row
    assert body["error_count"] == 1
    assert body["validation_errors"][0]["field"] == "origin"

    reports = await db_session.scalar(select(func.count()).select_from(PerformanceReport))
    assert reports == 2
    summaries = await db_session.scalar(select(func.count()).select_from(RouteSummary))
    assert summaries == 2


async def test_upload_xlsx_imports(client: AsyncClient) -> None:
    response = await client.post(
        _URL,
        files={
            "file": (
                "report.xlsx",
                samples.xlsx_bytes(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 201
    assert response.json()["imported_rows"] == 2


async def test_duplicate_upload_rejected(client: AsyncClient) -> None:
    files = {"file": ("r.csv", samples.csv_bytes(), "text/csv")}
    first = await client.post(_URL, files=files)
    assert first.status_code == 201

    second = await client.post(_URL, files={"file": ("r.csv", samples.csv_bytes(), "text/csv")})
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"


async def test_unsupported_extension_rejected(client: AsyncClient) -> None:
    response = await client.post(_URL, files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 415


async def test_missing_columns_marks_failed(client: AsyncClient) -> None:
    bad = b"Origin,Clicks\nJFK,10\n"
    response = await client.post(_URL, files={"file": ("bad.csv", bad, "text/csv")})

    assert response.status_code == 201
    body = response.json()
    assert body["upload_status"] == "failed"
    assert body["imported_rows"] == 0
    assert any(e["field"] == "columns" for e in body["validation_errors"])


async def test_list_and_get_and_delete(client: AsyncClient) -> None:
    created = await client.post(_URL, files={"file": ("r.csv", samples.csv_bytes(), "text/csv")})
    upload_id = created.json()["id"]

    listing = await client.get(_URL)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["id"] == upload_id

    detail = await client.get(f"{_URL}/{upload_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == upload_id

    deleted = await client.delete(f"{_URL}/{upload_id}")
    assert deleted.status_code == 204

    missing = await client.get(f"{_URL}/{upload_id}")
    assert missing.status_code == 404


async def test_delete_recomputes_summaries(client: AsyncClient, db_session: AsyncSession) -> None:
    created = await client.post(_URL, files={"file": ("r.csv", samples.csv_bytes(), "text/csv")})
    await client.delete(f"{_URL}/{created.json()['id']}")

    summaries = await db_session.scalar(select(func.count()).select_from(RouteSummary))
    assert summaries == 0
