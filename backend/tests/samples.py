"""Helpers to build sample KAYAK report files for tests."""

from __future__ import annotations

import csv
import io

from openpyxl import Workbook

HEADERS = [
    "Date",
    "Origin",
    "Destination",
    "Device",
    "Impressions",
    "Clicks",
    "CTR",
    "Avg CPC",
    "Spend",
    "Bookings",
    "Avg Position",
]

# Two valid rows, one blank row, one invalid row (bad origin code).
ROWS: list[list[object]] = [
    ["2026-07-01", "JFK", "LAX", "Desktop", "1,000", "50", "5.0%", "$1.20", "$60.00", "3", "2.1"],
    ["2026-07-01", "JFK", "SFO", "Mobile", "500", "20", "4.0%", "$1.10", "$22.00", "1", "3.4"],
    ["", "", "", "", "", "", "", "", "", "", ""],
    ["2026-07-02", "XX", "LAX", "Desktop", "100", "5", "5.0%", "$1.00", "$5.00", "0", "1.2"],
]


def _delimited_bytes(delimiter: str) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter)
    writer.writerow(HEADERS)
    writer.writerows(ROWS)
    return buffer.getvalue().encode("utf-8")


def csv_bytes() -> bytes:
    return _delimited_bytes(",")


def tsv_bytes() -> bytes:
    return _delimited_bytes("\t")


def xlsx_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(HEADERS)
    for row in ROWS:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
