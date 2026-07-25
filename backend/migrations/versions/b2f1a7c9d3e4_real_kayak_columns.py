"""real kayak columns: device 'all' segment + nullable bookings

Real KAYAK flight reports are not device-segmented and have no bookings column.
Add an ``all`` device segment and allow ``performance_reports.bookings`` to be
NULL so unavailable metrics are stored as NULL rather than fabricated.

Revision ID: b2f1a7c9d3e4
Revises: 59e19d3e8bf0
Create Date: 2026-07-25
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2f1a7c9d3e4"
down_revision: str | None = "59e19d3e8bf0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add the 'all' device segment (outside a transaction; PostgreSQL requires a
    # committed ADD VALUE before it can be used).
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE device_type ADD VALUE IF NOT EXISTS 'ALL'")

    # Bookings is optional in real reports -> allow NULL.
    op.alter_column(
        "performance_reports", "bookings", existing_type=sa.Integer(), nullable=True
    )


def downgrade() -> None:
    op.execute("UPDATE performance_reports SET bookings = 0 WHERE bookings IS NULL")
    op.alter_column(
        "performance_reports", "bookings", existing_type=sa.Integer(), nullable=False
    )
    # Note: PostgreSQL cannot drop an enum value; 'all' is intentionally retained.
