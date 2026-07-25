"""Aggregates all v1 application routes.

Mounted by ``app.api.router`` at the versioned ``API_V1_PREFIX`` (``/api/v1``).
Future business routers (reports, optimization, exports, …) are included here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import uploads, version

v1_router = APIRouter()
v1_router.include_router(version.router)
v1_router.include_router(uploads.router)
