"""Bid-file ingestion: validate, store, parse a KAYAK bid workbook.

Separate from the performance-report upload system (which is unchanged). Bid
files are .xlsx workbooks with Search Terms + Mode sheets.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError, UnsupportedMediaTypeError
from app.core.logging import get_logger
from app.domain.enums import FileType
from app.models.bid_file import BidFile, BidFileRoute
from app.optimizer.bid_file_parser import BidFileParser
from app.repositories.bid_file_repository import BidFileRepository, BidFileRouteRepository
from app.services import upload_validation

logger = get_logger("app.services.bid_file")


class BidFileService:
    """Create, list, and fetch bid files."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._files = BidFileRepository(session)
        self._routes = BidFileRouteRepository(session)
        self._parser = BidFileParser()

    async def create_bid_file(
        self, *, original_filename: str, content_type: str, data: bytes
    ) -> BidFile:
        file_type = upload_validation.resolve_file_type(original_filename)
        if file_type is not FileType.XLSX:
            raise UnsupportedMediaTypeError("bid files must be .xlsx workbooks")
        upload_validation.validate_size(len(data), settings.MAX_UPLOAD_SIZE_BYTES)
        upload_validation.validate_content(file_type, content_type, data)

        checksum = hashlib.sha256(data).hexdigest()
        existing = await self._files.get_by_checksum(checksum)
        if existing is not None:
            raise ConflictError(
                f"identical bid file already uploaded (id {existing.id})",
                details={"existing_bid_file_id": existing.id},
            )

        stored_name = f"{uuid.uuid4().hex}.xlsx"
        path = self._store(stored_name, data)
        parsed = self._parser.parse(path)

        bid_file = BidFile(
            provider_code=parsed.provider_code or "unknown",
            mode=parsed.mode,
            original_filename=original_filename,
            stored_filename=stored_name,
            checksum=checksum,
            file_type=file_type,
            file_size=len(data),
            route_count=len(parsed.routes),
        )
        await self._files.add(bid_file)

        await self._routes.bulk_add(
            [
                BidFileRoute(
                    bid_file_id=bid_file.id,
                    row_index=r.row_index,
                    provider_code=r.provider_code,
                    origin=r.origin,
                    destination=r.destination,
                    excluded=r.excluded,
                    current_override_cpc=r.override_cpc,
                    origin_is_iata=r.origin_is_iata,
                    destination_is_iata=r.destination_is_iata,
                )
                for r in parsed.routes
            ]
        )
        logger.info(
            "bid_file_created",
            bid_file_id=bid_file.id,
            provider=bid_file.provider_code,
            routes=bid_file.route_count,
        )
        return bid_file

    async def get_bid_file(self, bid_file_id: int) -> BidFile:
        bid_file = await self._files.get(bid_file_id)
        if bid_file is None:
            raise NotFoundError(f"bid file {bid_file_id} not found")
        return bid_file

    async def list_bid_files(self, *, limit: int, offset: int) -> tuple[list[BidFile], int]:
        files = await self._files.list_page(limit=limit, offset=offset)
        total = await self._files.count()
        return files, total

    def _store(self, stored_name: str, data: bytes) -> Path:
        directory = Path(settings.UPLOAD_DIR)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / stored_name
        path.write_bytes(data)
        return path
