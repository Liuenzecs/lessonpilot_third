"""teaching units

Revision ID: 0016
Revises: 0015_class_groups
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0016_teaching_units"
down_revision: str | None = "0015_class_groups"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "teaching_units",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("semester_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("topic_overview", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["semester_id"], ["semesters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teaching_units_semester_id", "teaching_units", ["semester_id"])

    op.add_column(
        "lesson_schedule_entries",
        sa.Column("unit_id", sa.String(36), nullable=True),
    )
    op.create_index(
        "ix_lesson_schedule_entries_unit_id",
        "lesson_schedule_entries",
        ["unit_id"],
    )
    op.create_foreign_key(
        "fk_lesson_schedule_entries_unit_id",
        "lesson_schedule_entries",
        "teaching_units",
        ["unit_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_lesson_schedule_entries_unit_id",
        "lesson_schedule_entries",
        type_="foreignkey",
    )
    op.drop_index("ix_lesson_schedule_entries_unit_id", "lesson_schedule_entries")
    op.drop_column("lesson_schedule_entries", "unit_id")
    op.drop_table("teaching_units")
