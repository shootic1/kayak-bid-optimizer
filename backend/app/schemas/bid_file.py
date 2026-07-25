"""Pydantic schemas for the bid-file API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import FileType


class BidFileRead(BaseModel):
    """A bid file record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_code: str
    mode: str
    original_filename: str
    file_type: FileType
    file_size: int
    route_count: int
    uploaded_at: datetime


class BidFileListResponse(BaseModel):
    """Paginated list of bid files."""

    items: list[BidFileRead]
    total: int
    limit: int
    offset: int
