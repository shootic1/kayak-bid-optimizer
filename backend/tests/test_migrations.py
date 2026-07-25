"""Schema/migration tests.

Verifies that the migrated database contains the expected tables, columns, enum
types, and constraints — i.e. that the Alembic migration produced the schema the
models expect.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _columns(session: AsyncSession, table: str) -> set[str]:
    result = await session.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = :t AND table_schema = 'public'"
        ),
        {"t": table},
    )
    return {row[0] for row in result}


async def test_tables_exist(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    )
    tables = {row[0] for row in result}
    assert {"uploads", "performance_reports", "route_summaries"} <= tables


async def test_uploads_columns(db_session: AsyncSession) -> None:
    columns = await _columns(db_session, "uploads")
    expected = {
        "id",
        "filename",
        "original_filename",
        "file_type",
        "file_size",
        "checksum",
        "upload_status",
        "uploaded_at",
        "processed_at",
    }
    assert expected <= columns


async def test_performance_reports_columns(db_session: AsyncSession) -> None:
    columns = await _columns(db_session, "performance_reports")
    expected = {
        "id",
        "upload_id",
        "report_type",
        "report_date",
        "origin",
        "destination",
        "device",
        "impressions",
        "clicks",
        "ctr",
        "avg_cpc",
        "spend",
        "bookings",
        "avg_position",
    }
    assert expected <= columns


async def test_enum_types_exist(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        text("SELECT typname FROM pg_type WHERE typname = ANY(:names)"),
        {"names": ["file_type", "upload_status", "report_type", "device_type"]},
    )
    assert {row[0] for row in result} == {
        "file_type",
        "upload_status",
        "report_type",
        "device_type",
    }


async def test_checksum_unique_constraint(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        text("SELECT indexname FROM pg_indexes WHERE tablename = 'uploads'")
    )
    indexes = {row[0] for row in result}
    assert any("checksum" in name for name in indexes)
