"""Unit tests for value normalizers."""

from __future__ import annotations

from datetime import date

import pytest

from app.domain.enums import DeviceType
from app.importers import normalizers


def test_normalize_airport_code_uppercases() -> None:
    assert normalizers.normalize_airport_code(" jfk ") == "JFK"


@pytest.mark.parametrize("bad", ["JF", "JFKK", "12A", "", None])
def test_normalize_airport_code_rejects_invalid(bad: object) -> None:
    with pytest.raises(ValueError, match="airport code"):
        normalizers.normalize_airport_code(bad)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-07-01", date(2026, 7, 1)),
        ("07/01/2026", date(2026, 7, 1)),
        (date(2026, 7, 1), date(2026, 7, 1)),
    ],
)
def test_normalize_date(value: object, expected: date) -> None:
    assert normalizers.normalize_date(value) == expected


def test_normalize_date_rejects_garbage() -> None:
    with pytest.raises(ValueError, match="date"):
        normalizers.normalize_date("not-a-date")


def test_normalize_int_handles_thousands_separator() -> None:
    assert normalizers.normalize_int("1,234") == 1234
    assert normalizers.normalize_int(42) == 42
    assert normalizers.normalize_int("10.0") == 10


def test_normalize_percentage_returns_fraction() -> None:
    assert normalizers.normalize_percentage("5.0%") == pytest.approx(0.05)
    assert normalizers.normalize_percentage(4.0) == pytest.approx(0.04)


def test_normalize_currency_strips_symbols() -> None:
    assert normalizers.normalize_currency("$1,234.56") == pytest.approx(1234.56)
    assert normalizers.normalize_currency("60") == pytest.approx(60.0)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Desktop", DeviceType.DESKTOP),
        ("mobile web", DeviceType.MOBILE),
        ("PC", DeviceType.DESKTOP),
    ],
)
def test_normalize_device(value: str, expected: DeviceType) -> None:
    assert normalizers.normalize_device(value) is expected


def test_normalize_device_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="device"):
        normalizers.normalize_device("tablet-xyz")
