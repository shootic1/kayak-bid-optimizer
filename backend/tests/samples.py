"""Sample report files for tests, using the REAL KAYAK report structure.

Inline and Dynamic Inline headers match actual KAYAK flight exports. A legacy
generic sample is also provided to exercise backward compatibility.
"""

from __future__ import annotations

import csv
import io

from openpyxl import Workbook

# --- Real KAYAK Inline report ------------------------------------------------
INLINE_HEADERS = [
    "Placement",
    "Origin",
    "Destination",
    "Advertiser Origin",
    "Advertiser Destination",
    "Average CPC (USD)",
    "Average Rank",
    "First Rank Bid (USD) 50% Share",
    "First Rank Bid (USD) 75% Share",
    "First Rank Bid (USD) 100% Share",
    "Second Rank Bid (USD) 50% Share",
    "Second Rank Bid (USD) 75% Share",
    "Second Rank Bid (USD) 100% Share",
    "Third Rank Bid (USD) 50% Share",
    "Third Rank Bid (USD) 75% Share",
    "Third Rank Bid (USD) 100% Share",
    "Est. Clicks",
    "Est. Impressions",
    "Est. Spend (USD)",
]

_INLINE_BIDS = ["1.40000000"] * 9


def _inline_row(origin: str, dest: str, cpc: str, rank: str, clicks: str, impr: str, spend: str):
    return [
        "CheapTicketsDealM_FIOAD_US",
        origin,
        dest,
        origin,
        dest,
        cpc,
        rank,
        *_INLINE_BIDS,
        clicks,
        impr,
        spend,
    ]


INLINE_ROWS: list[list[object]] = [
    _inline_row("JFK", "LAX", "1.40000000", "1.00000000", "50", "1000", "60.00000000"),
    _inline_row("JFK", "SFO", "1.10000000", "2.50000000", "20", "500", "22.00000000"),
    [""] * len(INLINE_HEADERS),  # blank row -> skipped
]

INVALID_INLINE_ROW = _inline_row("XX", "LAX", "1.40", "1.0", "5", "100", "5.00")  # bad origin


# --- Real KAYAK Dynamic Inline report ----------------------------------------
DYNAMIC_HEADERS = [
    "Placement",
    "Origin",
    "Destination",
    "Advertiser Origin",
    "Advertiser Destination",
    "Average CPC (USD)",
    "Average Inline Ad Rank",
    "Average Overall Position",
    "1st Overall Position Bid (USD)",
    "7th Overall Position Bid (USD)",
    "15th Overall Position Bid (USD)",
    "Bid To Be First Inline Ad",
    "Est. Clicks",
    "Est. Impressions",
    "Est. Spend (USD)",
]


def _dynamic_row(
    origin: str, dest: str, cpc: str, position: str, clicks: str, impr: str, spend: str
):
    return [
        "CheapTicketsDealD_FIOAD_US",
        origin,
        dest,
        origin,
        dest,
        cpc,
        "2.00000000",
        position,
        "3.15000000",
        "1.60000000",
        "1.60000000",
        "3.15000000",
        clicks,
        impr,
        spend,
    ]


DYNAMIC_ROWS: list[list[object]] = [
    _dynamic_row("ABE", "AUA", "1.60000000", "6.00000000", "0", "1", "0.00000000"),
    _dynamic_row("ABE", "MBJ", "1.60000000", "11.00000000", "3", "40", "4.80000000"),
    [""] * len(DYNAMIC_HEADERS),  # blank row -> skipped
]


# --- Legacy generic sample (backward compatibility) --------------------------
LEGACY_HEADERS = [
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

LEGACY_ROWS: list[list[object]] = [
    ["2026-07-01", "JFK", "LAX", "Desktop", "1000", "50", "5.0%", "$1.20", "$60.00", "3", "2.1"],
    ["2026-07-01", "JFK", "SFO", "Mobile", "500", "20", "4.0%", "$1.10", "$22.00", "1", "3.4"],
]


# --- Serialization helpers ---------------------------------------------------
def _delimited(headers: list[str], rows: list[list[object]], delimiter: str) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=delimiter)
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def inline_tsv_bytes() -> bytes:
    return _delimited(INLINE_HEADERS, INLINE_ROWS, "\t")


def dynamic_tsv_bytes() -> bytes:
    return _delimited(DYNAMIC_HEADERS, DYNAMIC_ROWS, "\t")


def legacy_csv_bytes() -> bytes:
    return _delimited(LEGACY_HEADERS, LEGACY_ROWS, ",")


def inline_xlsx_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(INLINE_HEADERS)
    for row in INLINE_ROWS:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
