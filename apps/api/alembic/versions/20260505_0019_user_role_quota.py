"""user role + is_disabled fields

Revision ID: 0019
Revises: 0018_cost_logs
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0019_user_role_quota"
down_revision: str | None = "0018_cost_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(16), nullable=False, server_default="teacher"))
    op.add_column("users", sa.Column("is_disabled", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("disabled_reason", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "disabled_reason")
    op.drop_column("users", "disabled_at")
    op.drop_column("users", "is_disabled")
    op.drop_column("users", "role")
