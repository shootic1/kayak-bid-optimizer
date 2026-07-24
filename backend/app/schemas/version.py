"""Pydantic response schema for the version endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VersionResponse(BaseModel):
    """Application version and runtime environment metadata."""

    name: str = Field(examples=["KAYAK Bid Optimizer Pro"])
    version: str = Field(examples=["1.0.0"])
    environment: str = Field(examples=["development"])
