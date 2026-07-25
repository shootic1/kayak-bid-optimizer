"""Bid-file API — upload/list/fetch KAYAK bid workbooks."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestError, PayloadTooLargeError
from app.database.session import get_db_session
from app.schemas.bid_file import BidFileListResponse, BidFileRead
from app.services.bid_file_service import BidFileService

router = APIRouter(prefix="/bid-files", tags=["bid-files"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def _read_within_limit(file: UploadFile, max_size: int) -> bytes:
    data = await file.read(max_size + 1)
    if len(data) > max_size:
        raise PayloadTooLargeError(f"file exceeds the maximum allowed size of {max_size} bytes")
    return data


@router.post(
    "",
    response_model=BidFileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a KAYAK bid workbook",
)
async def create_bid_file(
    session: DbSession,
    file: Annotated[UploadFile, File(description="A KAYAK bid .xlsx workbook.")],
) -> BidFileRead:
    if not file.filename:
        raise BadRequestError("a filename is required")
    data = await _read_within_limit(file, settings.MAX_UPLOAD_SIZE_BYTES)
    bid_file = await BidFileService(session).create_bid_file(
        original_filename=file.filename,
        content_type=file.content_type or "",
        data=data,
    )
    await session.commit()
    await session.refresh(bid_file)
    return BidFileRead.model_validate(bid_file)


@router.get("", response_model=BidFileListResponse, summary="List bid files")
async def list_bid_files(
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> BidFileListResponse:
    files, total = await BidFileService(session).list_bid_files(limit=limit, offset=offset)
    return BidFileListResponse(
        items=[BidFileRead.model_validate(f) for f in files],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{bid_file_id}", response_model=BidFileRead, summary="Get a bid file")
async def get_bid_file(session: DbSession, bid_file_id: int) -> BidFileRead:
    bid_file = await BidFileService(session).get_bid_file(bid_file_id)
    return BidFileRead.model_validate(bid_file)
