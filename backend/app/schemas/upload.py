"""Pydantic schemas for the upload API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import FileType, UploadStatus


class UploadValidationError(BaseModel):
    """A single row-level validation error surfaced to the client."""

    row: int
    field: str
    message: str


class UploadBase(BaseModel):
    """Fields common to list and detail representations of an upload."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    file_type: FileType
    file_size: int
    checksum: str
    upload_status: UploadStatus
    report_type: str | None
    imported_rows: int
    skipped_rows: int
    error_count: int
    processing_ms: int | None
    uploaded_at: datetime
    processed_at: datetime | None


class UploadListItem(UploadBase):
    """Compact representation for the upload history table."""


class UploadDetail(UploadBase):
    """Full representation including per-row validation errors."""

    error_message: str | None
    validation_errors: list[UploadValidationError]


class UploadListResponse(BaseModel):
    """Paginated list of uploads."""

    items: list[UploadListItem]
    total: int
    limit: int
    offset: int


class ImportSummary(BaseModel):
    """Outcome of importing a single upload."""

    upload_id: int
    status: UploadStatus
    report_type: str | None
    imported_rows: int
    skipped_rows: int
    error_count: int
    processing_ms: int | None
    validation_errors: list[UploadValidationError] = Field(default_factory=list)
