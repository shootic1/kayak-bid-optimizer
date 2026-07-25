"""ORM models.

Importing this package registers every model on ``Base.metadata`` so Alembic
autogenerate and ``create_all`` can see them.
"""

from __future__ import annotations

from app.database.base import Base
from app.models.performance_report import PerformanceReport
from app.models.route_summary import RouteSummary
from app.models.upload import Upload

__all__ = ["Base", "PerformanceReport", "RouteSummary", "Upload"]
