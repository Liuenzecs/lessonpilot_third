"""drop zombie billing/subscription tables (no Python models exist for these)

Revision ID: 0020
Revises: 0019_user_role_quota
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020_cleanup_zombie_tables"
down_revision: str | None = "0019_user_role_quota"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Drop order matters: billing_orders has FK → user_subscriptions, so drop billing_orders first
ZOMBIE_TABLES = [
    "billing_webhook_events",
    "invoice_requests",
    "billing_orders",
    "user_subscriptions",
    "quota_adjustments",
    "email_delivery_logs",
]


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    for table in ZOMBIE_TABLES:
        if _has_table(table):
            op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


def downgrade() -> None:
    # No downgrade — these tables should not be recreated.
    # The original migrations that created them are still available for reference.
    pass
