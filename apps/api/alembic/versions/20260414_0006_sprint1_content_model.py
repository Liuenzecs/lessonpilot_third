"""Sprint 1: content model overhaul

Revision ID: 20260414_0006
Revises: 20260412_0005
Create Date: 2026-04-14

- tasks: add scene, lesson_type, class_hour, lesson_category columns
- documents: drop unique constraint on task_id (keep index for 1:many)
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260414_0006"
down_revision = "20260412_0005"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _has_constraint(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for constraint in inspector.get_unique_constraints(table_name):
        if constraint["name"] == constraint_name:
            return True
    return False


def upgrade() -> None:
    # tasks: add new columns (idempotent)
    if not _has_column("tasks", "scene"):
        op.add_column("tasks", sa.Column("scene", sa.String(32), nullable=False, server_default="public_school"))
    if not _has_column("tasks", "lesson_type"):
        op.add_column("tasks", sa.Column("lesson_type", sa.String(32), nullable=False, server_default="lesson_plan"))
    if not _has_column("tasks", "class_hour"):
        op.add_column("tasks", sa.Column("class_hour", sa.Integer(), nullable=False, server_default="1"))
    if not _has_column("tasks", "lesson_category"):
        op.add_column("tasks", sa.Column("lesson_category", sa.String(32), nullable=False, server_default="new"))

    # documents: drop unique constraint on task_id to allow 1:many
    # The unique constraint name varies by dialect; try the common name patterns
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for constraint in inspector.get_unique_constraints("documents"):
        if "task_id" in constraint.get("column_names", []):
            constraint_name = constraint.get("name")
            if constraint_name:
                op.drop_constraint(constraint_name, "documents", type_="unique")
                break


def downgrade() -> None:
    # Re-add unique constraint on documents.task_id
    op.create_unique_constraint("uq_documents_task_id", "documents", ["task_id"])

    # Remove new columns from tasks
    op.drop_column("tasks", "lesson_category")
    op.drop_column("tasks", "class_hour")
    op.drop_column("tasks", "lesson_type")
    op.drop_column("tasks", "scene")
