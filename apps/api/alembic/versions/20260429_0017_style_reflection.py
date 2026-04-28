"""style samples + teaching reflections

Revision ID: 0017
Revises: 0016_teaching_units
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0017_style_reflection"
down_revision: str | None = "0016_teaching_units"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "style_samples",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("subject", sa.String(80), nullable=False),
        sa.Column("grade", sa.String(80), nullable=False),
        sa.Column("section_key", sa.String(80), nullable=False),
        sa.Column("original_content", sa.Text(), nullable=True),
        sa.Column("confirmed_content", sa.Text(), nullable=True),
        sa.Column("diff_summary", sa.Text(), nullable=True),
        sa.Column("extracted_patterns", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_style_samples_user_id", "style_samples", ["user_id"])
    op.create_index("ix_style_samples_document_id", "style_samples", ["document_id"])

    op.create_table(
        "teaching_reflections",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("goal_achievement", sa.Integer(), nullable=False),
        sa.Column("difficulty_handling", sa.Text(), nullable=True),
        sa.Column("student_response", sa.Text(), nullable=True),
        sa.Column("time_feedback", sa.Text(), nullable=True),
        sa.Column("improvement_notes", sa.Text(), nullable=True),
        sa.Column("free_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teaching_reflections_task_id", "teaching_reflections", ["task_id"])
    op.create_index("ix_teaching_reflections_user_id", "teaching_reflections", ["user_id"])


def downgrade() -> None:
    op.drop_table("teaching_reflections")
    op.drop_table("style_samples")
