"""phase0 initial tables

Revision ID: 20260410_0001
Revises:
Create Date: 2026-04-10 23:50:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260410_0001"
down_revision = None
branch_labels = None
depends_on = None


def _uuid_type() -> sa.TypeEngine:
    return sa.String(length=36)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("user_id", _uuid_type(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=80), nullable=False),
        sa.Column("grade", sa.String(length=80), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", _uuid_type(), nullable=False),
        sa.Column("task_id", _uuid_type(), nullable=False),
        sa.Column("user_id", _uuid_type(), nullable=False),
        sa.Column("doc_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id"),
    )
    op.create_index("ix_documents_task_id", "documents", ["task_id"], unique=False)
    op.create_index("ix_documents_user_id", "documents", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_index("ix_documents_task_id", table_name="documents")
    op.drop_table("documents")
    op.drop_index("ix_tasks_user_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
