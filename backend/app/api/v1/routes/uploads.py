"""Upload API — create, list, fetch, and delete uploads."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestError, PayloadTooLargeError
from app.database.session import get_db_session
from app.schemas.upload import UploadDetail, UploadListItem, UploadListResponse
from app.services.import_service import ImportService
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def _read_within_limit(file: UploadFile, max_size: int) -> bytes:
    """Read the upload, rejecting anything larger than ``max_size`` bytes."""
    data = await file.read(max_size + 1)
    if len(data) > max_size:
        raise PayloadTooLargeError(f"file exceeds the maximum allowed size of {max_size} bytes")
    return data


@router.post(
    "",
    response_model=UploadDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and import a KAYAK report",
)
async def create_upload(
    session: DbSession,
    file: Annotated[UploadFile, File(description="An .xlsx, .csv, or .tsv report file.")],
) -> UploadDetail:
    """Accept a report file, validate it, store it, and import its rows."""
    if not file.filename:
        raise BadRequestError("a filename is required")

    data = await _read_within_limit(file, settings.MAX_UPLOAD_SIZE_BYTES)

    upload_service = UploadService(session)
    import_service = ImportService(session)

    upload = await upload_service.create_upload(
        original_filename=file.filename,
        content_type=file.content_type or "",
        data=data,
    )
    await import_service.process_upload(upload)
    await session.commit()
    await session.refresh(upload)
    return UploadDetail.model_validate(upload)


@router.get("", response_model=UploadListResponse, summary="List uploads (history)")
async def list_uploads(
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UploadListResponse:
    """Return uploads newest-first with pagination metadata."""
    uploads, total = await UploadService(session).list_uploads(limit=limit, offset=offset)
    return UploadListResponse(
        items=[UploadListItem.model_validate(u) for u in uploads],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{upload_id}", response_model=UploadDetail, summary="Get an upload")
async def get_upload(session: DbSession, upload_id: int) -> UploadDetail:
    """Return a single upload, including per-row validation errors."""
    upload = await UploadService(session).get_upload(upload_id)
    return UploadDetail.model_validate(upload)


@router.delete(
    "/{upload_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an upload and its imported data",
)
async def delete_upload(session: DbSession, upload_id: int) -> Response:
    """Delete an upload, its stored file, its rows, and refresh route summaries."""
    await UploadService(session).delete_upload(upload_id)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
