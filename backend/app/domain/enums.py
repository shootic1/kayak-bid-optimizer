"""Domain enumerations shared across models, schemas, and services.

Framework-free ``StrEnum`` types so they serialize cleanly to JSON and map
directly to native PostgreSQL enum values.
"""

from __future__ import annotations

from enum import StrEnum


class FileType(StrEnum):
    """Accepted upload file types."""

    XLSX = "xlsx"
    CSV = "csv"
    TSV = "tsv"


class UploadStatus(StrEnum):
    """Lifecycle status of an upload and its processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportType(StrEnum):
    """KAYAK report variants."""

    INLINE = "inline"
    DYNAMIC_INLINE = "dynamic_inline"


class DeviceType(StrEnum):
    """Device segment of a performance row."""

    DESKTOP = "desktop"
    MOBILE = "mobile"


# Mapping of file extension (without dot) to FileType.
EXTENSION_TO_FILE_TYPE: dict[str, FileType] = {
    "xlsx": FileType.XLSX,
    "csv": FileType.CSV,
    "tsv": FileType.TSV,
}
