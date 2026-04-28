"""question bank

Revision ID: 0012
Revises: 0011
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0012_question_bank"
down_revision: str | None = "0011_teacher_style_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("chapter", sa.String(), nullable=False),
        sa.Column("grade", sa.String(), nullable=False),
        sa.Column("question_type", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(), nullable=False),
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("answer", sa.String(), nullable=False),
        sa.Column("analysis", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_questions_chapter", "questions", ["chapter"])


def downgrade() -> None:
    op.drop_index("ix_questions_chapter", table_name="questions")
    op.drop_table("questions")
