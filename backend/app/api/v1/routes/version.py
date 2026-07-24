"""Versioned application route — ``GET /api/v1/version``."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.version import VersionResponse

router = APIRouter(tags=["meta"])


@router.get("/version", response_model=VersionResponse, summary="Application version")
async def version() -> VersionResponse:
    """Return the application name, version, and active environment."""
    return VersionResponse(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.NODE_ENV,
    )
