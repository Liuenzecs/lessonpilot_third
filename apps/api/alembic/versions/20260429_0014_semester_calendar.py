"""semester calendar

Revision ID: 0014
Revises: 0013_share_links
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0014_semester_calendar"
down_revision: str | None = "0013_share_links"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "semesters",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("grade", sa.String(80), nullable=False),
        sa.Column("subject", sa.String(80), nullable=False),
        sa.Column("week_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_semesters_user_id", "semesters", ["user_id"])

    op.create_table(
        "week_schedules",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("semester_id", sa.String(36), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["semester_id"], ["semesters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_week_schedules_semester_id", "week_schedules", ["semester_id"])

    op.create_table(
        "lesson_schedule_entries",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("week_schedule_id", sa.String(36), nullable=False),
        sa.Column("task_id", sa.String(36), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("class_period", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["week_schedule_id"], ["week_schedules.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lesson_schedule_entries_week_schedule_id", "lesson_schedule_entries", ["week_schedule_id"])
    op.create_index("ix_lesson_schedule_entries_task_id", "lesson_schedule_entries", ["task_id"])


def downgrade() -> None:
    op.drop_table("lesson_schedule_entries")
    op.drop_table("week_schedules")
    op.drop_table("semesters")
