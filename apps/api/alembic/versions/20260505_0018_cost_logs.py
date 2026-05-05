"""cost_logs table for LLM token / cost tracking

Revision ID: 0018
Revises: 0017_style_reflection
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0018_cost_logs"
down_revision: str | None = "0017_style_reflection"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cost_logs",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("model", sa.String(40), nullable=False),
        sa.Column("operation", sa.String(20), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False),
        sa.Column("completion_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_cny", sa.Float(), nullable=False),
        sa.Column("task_id", sa.String(36), nullable=True),
        sa.Column("doc_type", sa.String(20), nullable=True),
        sa.Column("section_name", sa.String(40), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cost_logs_user_created", "cost_logs", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_cost_logs_user_created", table_name="cost_logs")
    op.drop_table("cost_logs")
