"""Application configuration.

Settings are loaded from environment variables (and an optional local ``.env``
file) using ``pydantic-settings``. This is the single source of truth for
runtime configuration — no other module should read ``os.environ`` directly.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production", "test"]


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Every value has a safe development default so the application can boot in a
    fresh checkout without a hand-written ``.env`` file. Production deployments
    are expected to override the sensitive values (notably ``DATABASE_URL``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application metadata -------------------------------------------------
    APP_NAME: str = "KAYAK Bid Optimizer Pro"
    APP_VERSION: str = "1.0.0"
    SERVICE_NAME: str = "backend"
    NODE_ENV: Environment = "development"

    # --- HTTP server ----------------------------------------------------------
    # Unversioned base for infrastructure endpoints (health/readiness).
    API_PREFIX: str = "/api"
    # Versioned namespace for application endpoints (see ADR-0004).
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Comma-separated list of allowed CORS origins for the browser frontend.
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Database -------------------------------------------------------------
    # Async SQLAlchemy URL. The default targets the docker-compose ``db`` host;
    # override for local runs (e.g. ``...@localhost:5432/...``).
    DATABASE_URL: str = "postgresql+asyncpg://kayak:kayak@localhost:5432/kayak_bid_optimizer"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    # Fail fast on the readiness probe instead of hanging on a dead database.
    DB_CONNECT_TIMEOUT_SECONDS: float = 5.0

    # --- File uploads ---------------------------------------------------------
    # Directory where uploaded source files are stored (mounted volume in prod).
    UPLOAD_DIR: str = "storage/uploads"
    # Maximum accepted upload size in bytes (default 25 MiB).
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024

    # --- Logging --------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    # ``json`` for production/aggregators, ``console`` for readable local dev.
    LOG_FORMAT: Literal["json", "console"] = "console"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse ``CORS_ORIGINS`` into a clean list of origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        return self.NODE_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    Cached so configuration is parsed once per process. Use FastAPI's
    dependency injection (``Depends(get_settings)``) or import this function
    directly rather than constructing ``Settings`` ad hoc.
    """
    return Settings()


settings = get_settings()
