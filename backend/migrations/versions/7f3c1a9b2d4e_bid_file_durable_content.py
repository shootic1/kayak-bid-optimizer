"""bid file durable content

Persist the uploaded bid workbook bytes on ``bid_files.content`` so exports can
rebuild the workbook after a container restart. The local ``UPLOAD_DIR`` is
ephemeral on Railway, so files written at upload time are lost on redeploy while
the run/recommendation rows survive in Postgres. Nullable: pre-existing rows have
no stored bytes (their files are already gone) and simply cannot be re-exported.

Revision ID: 7f3c1a9b2d4e
Revises: 63fed26e1c8e
Create Date: 2026-07-26 05:45:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7f3c1a9b2d4e"
down_revision: str | None = "63fed26e1c8e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bid_files", sa.Column("content", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("bid_files", "content")
