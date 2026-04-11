"""phase2 document snapshots

Revision ID: 20260411_0002
Revises: 20260410_0001
Create Date: 2026-04-11 22:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260411_0002"
down_revision = "20260410_0001"
branch_labels = None
depends_on = None


def _uuid_type() -> sa.TypeEngine:
    return sa.String(length=36)


def upgrade() -> None:
    op.create_table(
        "document_snapshots",
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("document_id", _uuid_type(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_document_snapshots_document_id",
        "document_snapshots",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_document_snapshots_document_id", table_name="document_snapshots")
    op.drop_table("document_snapshots")
