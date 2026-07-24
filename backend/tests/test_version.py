"""Integration tests for the versioned meta endpoints."""

from __future__ import annotations

from httpx import AsyncClient


async def test_version_returns_metadata(client: AsyncClient) -> None:
    """`GET /api/v1/version` returns application name, version, and environment."""
    response = await client.get("/api/v1/version")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "KAYAK Bid Optimizer Pro"
    assert body["version"] == "1.0.0"
    assert "environment" in body


async def test_unknown_route_returns_structured_404(client: AsyncClient) -> None:
    """Unknown routes return the canonical structured error envelope."""
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
