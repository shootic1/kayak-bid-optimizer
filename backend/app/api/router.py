"""Top-level API router.

Composes the unversioned infrastructure routes (health/readiness) with the
versioned ``/api/v1`` application namespace. ``app.main`` includes this router.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api import health
from app.api.v1.router import v1_router
from app.core.config import settings

api_router = APIRouter()

# Unversioned infrastructure endpoints: /api/health, /api/health/ready
api_router.include_router(health.router, prefix=settings.API_PREFIX)

# Versioned application endpoints: /api/v1/...
api_router.include_router(v1_router, prefix=settings.API_V1_PREFIX)
