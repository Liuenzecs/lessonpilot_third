"""phase3 auth and account tables

Revision ID: 20260411_0003
Revises: 20260411_0002
Create Date: 2026-04-11 23:40:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260411_0003"
down_revision = "20260411_0002"
branch_labels = None
depends_on = None


def _uuid_type() -> sa.TypeEngine:
    return sa.String(length=36)


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    if not _has_column("users", "email_verified"):
        op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
        op.alter_column("users", "email_verified", server_default=None)

    if not _has_column("users", "email_verified_at"):
        op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))

    if not _has_table("auth_tokens"):
        op.create_table(
            "auth_tokens",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=False),
            sa.Column("token_hash", sa.String(length=128), nullable=False),
            sa.Column("token_type", sa.String(length=32), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("token_hash"),
        )

    if not _has_index("auth_tokens", "ix_auth_tokens_user_id"):
        op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"], unique=False)

    if not _has_index("auth_tokens", "ix_auth_tokens_token_hash"):
        op.create_index("ix_auth_tokens_token_hash", "auth_tokens", ["token_hash"], unique=False)

    if not _has_index("auth_tokens", "ix_auth_tokens_token_type"):
        op.create_index("ix_auth_tokens_token_type", "auth_tokens", ["token_type"], unique=False)

    if not _has_table("feedback_entries"):
        op.create_table(
            "feedback_entries",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=False),
            sa.Column("mood", sa.String(length=16), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("page_path", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_index("feedback_entries", "ix_feedback_entries_user_id"):
        op.create_index("ix_feedback_entries_user_id", "feedback_entries", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_feedback_entries_user_id", table_name="feedback_entries")
    op.drop_table("feedback_entries")

    op.drop_index("ix_auth_tokens_token_type", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_token_hash", table_name="auth_tokens")
    op.drop_index("ix_auth_tokens_user_id", table_name="auth_tokens")
    op.drop_table("auth_tokens")

    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "email_verified")
