"""Upload orchestration: validate, store, deduplicate, and manage uploads."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.domain.enums import UploadStatus
from app.models.upload import Upload
from app.repositories.performance_report_repository import PerformanceReportRepository
from app.repositories.route_summary_repository import RouteSummaryRepository
from app.repositories.upload_repository import UploadRepository
from app.services import upload_validation

logger = get_logger("app.services.upload")


class UploadService:
    """Create, list, fetch, and delete uploads (processing lives in ImportService)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._uploads = UploadRepository(session)
        self._reports = PerformanceReportRepository(session)
        self._summaries = RouteSummaryRepository(session)

    async def create_upload(
        self, *, original_filename: str, content_type: str, data: bytes
    ) -> Upload:
        """Validate and persist an upload; return the pending record.

        Raises typed errors for unsupported type (415), oversize (413), invalid
        content (415), or duplicate checksum (409).
        """
        file_type = upload_validation.resolve_file_type(original_filename)
        upload_validation.validate_size(len(data), settings.MAX_UPLOAD_SIZE_BYTES)
        upload_validation.validate_content(file_type, content_type, data)

        checksum = hashlib.sha256(data).hexdigest()
        existing = await self._uploads.get_by_checksum(checksum)
        if existing is not None:
            raise ConflictError(
                f"identical file already uploaded (id {existing.id})",
                details={"existing_upload_id": existing.id},
            )

        stored_name = f"{uuid.uuid4().hex}.{file_type.value}"
        self._write_file(stored_name, data)

        upload = Upload(
            filename=stored_name,
            original_filename=original_filename,
            file_type=file_type,
            file_size=len(data),
            checksum=checksum,
            upload_status=UploadStatus.PENDING,
        )
        await self._uploads.add(upload)
        logger.info("upload_created", upload_id=upload.id, filename=original_filename)
        return upload

    async def get_upload(self, upload_id: int) -> Upload:
        upload = await self._uploads.get(upload_id)
        if upload is None:
            raise NotFoundError(f"upload {upload_id} not found")
        return upload

    async def list_uploads(self, *, limit: int, offset: int) -> tuple[list[Upload], int]:
        uploads = await self._uploads.list(limit=limit, offset=offset)
        total = await self._uploads.count()
        return uploads, total

    async def delete_upload(self, upload_id: int) -> None:
        """Delete an upload, its file, its reports, and refresh route summaries."""
        upload = await self.get_upload(upload_id)

        # Capture affected route segments before the cascade delete.
        segments = await self._reports.segments_for_upload(upload_id)

        self._remove_file(upload.filename)
        await self._uploads.delete(upload)
        await self._summaries.recompute_segments(segments)
        logger.info("upload_deleted", upload_id=upload_id)

    # --- file storage --------------------------------------------------------
    def _upload_dir(self) -> Path:
        path = Path(settings.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _write_file(self, stored_name: str, data: bytes) -> None:
        (self._upload_dir() / stored_name).write_bytes(data)

    def _remove_file(self, stored_name: str) -> None:
        target = self._upload_dir() / stored_name
        target.unlink(missing_ok=True)
