"""Parser tests for Excel, CSV, and TSV."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests import samples

from app.domain.enums import FileType
from app.importers.base import ParseError
from app.importers.delimited_parser import CsvParser, TsvParser
from app.importers.excel_parser import ExcelParser
from app.importers.factory import get_parser


def test_factory_returns_correct_parser() -> None:
    assert isinstance(get_parser(FileType.XLSX), ExcelParser)
    assert isinstance(get_parser(FileType.CSV), CsvParser)
    assert isinstance(get_parser(FileType.TSV), TsvParser)


def test_csv_parser_reads_headers_and_rows(tmp_path: Path) -> None:
    path = tmp_path / "report.csv"
    path.write_bytes(samples.csv_bytes())

    table = CsvParser().parse(path)

    assert table.headers == samples.HEADERS
    assert len(table.rows) == len(samples.ROWS)
    assert table.rows[0]["Origin"] == "JFK"


def test_tsv_parser_reads_rows(tmp_path: Path) -> None:
    path = tmp_path / "report.tsv"
    path.write_bytes(samples.tsv_bytes())

    table = TsvParser().parse(path)

    assert table.headers == samples.HEADERS
    assert table.rows[1]["Destination"] == "SFO"


def test_excel_parser_reads_rows(tmp_path: Path) -> None:
    path = tmp_path / "report.xlsx"
    path.write_bytes(samples.xlsx_bytes())

    table = ExcelParser().parse(path)

    assert table.headers == samples.HEADERS
    assert table.rows[0]["Origin"] == "JFK"


def test_excel_parser_rejects_non_excel(tmp_path: Path) -> None:
    path = tmp_path / "bad.xlsx"
    path.write_bytes(b"this is not a zip archive")
    with pytest.raises(ParseError):
        ExcelParser().parse(path)
