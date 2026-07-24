"""Model exports.

Re-exports the declarative ``Base`` so future ORM models can import it from a
stable ``app.models`` location. No business models are defined in Phase 1.
"""

from __future__ import annotations

from app.database.base import Base

__all__ = ["Base"]
