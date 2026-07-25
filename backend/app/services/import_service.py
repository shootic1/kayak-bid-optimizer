"""Import engine — turns a stored upload into normalized, persisted report rows."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.enums import UploadStatus
from app.importers.base import ParseError
from app.importers.detection import detect_report
from app.importers.factory import get_parser
from app.importers.row_mapper import NormalizedRow, RowError, RowMappingError, is_blank_row, map_row
from app.models.performance_report import PerformanceReport
from app.models.upload import Upload
from app.repositories.performance_report_repository import PerformanceReportRepository
from app.repositories.route_summary_repository import RouteSummaryRepository

logger = get_logger("app.services.import")

# Data rows start at spreadsheet line 2 (line 1 is the header).
_FIRST_DATA_ROW = 2


class ImportService:
    """Processes a single upload: parse, validate, normalize, persist, aggregate."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._reports = PerformanceReportRepository(session)
        self._summaries = RouteSummaryRepository(session)

    async def process_upload(self, upload: Upload) -> Upload:
        """Import an upload, updating its status and metrics in place."""
        start = time.perf_counter()
        upload.upload_status = UploadStatus.PROCESSING
        await self._session.flush()

        try:
            return await self._process(upload, start)
        except Exception as exc:  # defensive: never leave an upload stuck PROCESSING
            logger.error("import_failed", upload_id=upload.id, error=str(exc), exc_info=exc)
            self._finalize(upload, UploadStatus.FAILED, start, error_message=str(exc))
            await self._session.flush()
            return upload

    async def _process(self, upload: Upload, start: float) -> Upload:
        path = Path(settings.UPLOAD_DIR) / upload.filename
        parser = get_parser(upload.file_type)

        try:
            table = parser.parse(path)
        except ParseError as exc:
            self._finalize(upload, UploadStatus.FAILED, start, error_message=str(exc))
            await self._session.flush()
            return upload

        detection = detect_report(table.headers, upload.original_filename)
        upload.report_type = detection.report_type.value
        if not detection.is_valid:
            upload.validation_errors = [
                RowError(0, "columns", message).as_dict() for message in detection.errors
            ]
            self._finalize(
                upload,
                UploadStatus.FAILED,
                start,
                error_message="; ".join(detection.errors),
            )
            await self._session.flush()
            return upload

        reports: list[PerformanceReport] = []
        errors: list[RowError] = []
        skipped = 0
        segments: set[tuple[str, str, object]] = set()

        for line_no, raw in enumerate(table.rows, start=_FIRST_DATA_ROW):
            if is_blank_row(raw, detection):
                skipped += 1
                continue
            try:
                normalized = map_row(raw, detection)
            except RowMappingError as exc:
                errors.append(RowError(line_no, exc.field, exc.message))
                skipped += 1
                continue
            reports.append(self._to_model(upload.id, normalized))
            segments.add((normalized.origin, normalized.destination, normalized.device))

        await self._reports.bulk_add(reports)
        await self._summaries.recompute_segments(segments)  # type: ignore[arg-type]

        upload.imported_rows = len(reports)
        upload.skipped_rows = skipped
        upload.validation_errors = [e.as_dict() for e in errors]
        self._finalize(upload, UploadStatus.COMPLETED, start)
        await self._session.flush()

        logger.info(
            "import_completed",
            upload_id=upload.id,
            report_type=upload.report_type,
            imported=upload.imported_rows,
            skipped=upload.skipped_rows,
            errors=len(errors),
            duration_ms=upload.processing_ms,
        )
        return upload

    @staticmethod
    def _to_model(upload_id: int, row: NormalizedRow) -> PerformanceReport:
        return PerformanceReport(
            upload_id=upload_id,
            report_type=row.report_type,
            report_date=row.report_date,
            origin=row.origin,
            destination=row.destination,
            device=row.device,
            impressions=row.impressions,
            clicks=row.clicks,
            ctr=row.ctr,
            avg_cpc=row.avg_cpc,
            spend=row.spend,
            bookings=row.bookings,
            avg_position=row.avg_position,
        )

    @staticmethod
    def _finalize(
        upload: Upload,
        status: UploadStatus,
        start: float,
        *,
        error_message: str | None = None,
    ) -> None:
        upload.upload_status = status
        upload.error_message = error_message
        upload.processed_at = datetime.now(UTC)
        upload.processing_ms = int((time.perf_counter() - start) * 1000)
