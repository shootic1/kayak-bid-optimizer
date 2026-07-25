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
    """Device segment of a performance row.

    Real KAYAK flight reports are not device-segmented, so ``ALL`` is used when a
    report has no device column. ``DESKTOP``/``MOBILE`` remain supported for
    reports (or future exports) that do segment by device.
    """

    ALL = "all"
    DESKTOP = "desktop"
    MOBILE = "mobile"


# Mapping of file extension (without dot) to FileType.
EXTENSION_TO_FILE_TYPE: dict[str, FileType] = {
    "xlsx": FileType.XLSX,
    "csv": FileType.CSV,
    "tsv": FileType.TSV,
}


class MatchStatus(StrEnum):
    """Outcome of matching a bid-file route to historical performance."""

    MATCHED = "matched"
    UNMATCHED_NO_HISTORY = "unmatched_no_history"
    UNMATCHED_NON_IATA = "unmatched_non_iata"
    SKIPPED_EXCLUDED = "skipped_excluded"


class RunStatus(StrEnum):
    """Lifecycle status of an optimization run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RecommendationAction(StrEnum):
    """The only actions the deterministic engine may produce."""

    KEEP = "keep"
    INCREASE = "increase"
    MANUAL_REVIEW = "manual_review"
    INSUFFICIENT_DATA = "insufficient_data"


class ConfidenceLevel(StrEnum):
    """Confidence in a recommendation, from data volume."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
