"""Shared SQLAlchemy column type instances.

Native PostgreSQL ENUM types are defined **once** here and reused across models
so each type is created a single time in migrations (e.g. ``device_type`` is
referenced by both ``performance_reports`` and ``route_summaries``).
"""

from __future__ import annotations

from sqlalchemy import Enum

from app.domain.enums import DeviceType, FileType, ReportType, UploadStatus

file_type_enum = Enum(FileType, name="file_type", native_enum=True)
upload_status_enum = Enum(UploadStatus, name="upload_status", native_enum=True)
report_type_enum = Enum(ReportType, name="report_type", native_enum=True)
device_type_enum = Enum(DeviceType, name="device_type", native_enum=True)
