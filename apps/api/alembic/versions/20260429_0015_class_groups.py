"""class groups + task variant fields

Revision ID: 0015
Revises: 0014_semester_calendar
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0015_class_groups"
down_revision: str | None = "0014_semester_calendar"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "class_groups",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("level", sa.String(32), nullable=False, server_default="standard"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_class_groups_user_id", "class_groups", ["user_id"])

    op.add_column("tasks", sa.Column("base_task_id", sa.String(36), nullable=True))
    op.add_column("tasks", sa.Column("class_group_id", sa.String(36), nullable=True))
    op.create_index("ix_tasks_base_task_id", "tasks", ["base_task_id"])
    op.create_index("ix_tasks_class_group_id", "tasks", ["class_group_id"])
    op.create_foreign_key(
        "fk_tasks_base_task_id",
        "tasks",
        "tasks",
        ["base_task_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_class_group_id",
        "tasks",
        "class_groups",
        ["class_group_id"],
        ["id"],
    )

    op.add_column(
        "lesson_schedule_entries",
        sa.Column("class_group_id", sa.String(36), nullable=True),
    )
    op.create_index(
        "ix_lesson_schedule_entries_class_group_id",
        "lesson_schedule_entries",
        ["class_group_id"],
    )
    op.create_foreign_key(
        "fk_lesson_schedule_entries_class_group_id",
        "lesson_schedule_entries",
        "class_groups",
        ["class_group_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_lesson_schedule_entries_class_group_id",
        "lesson_schedule_entries",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_lesson_schedule_entries_class_group_id",
        "lesson_schedule_entries",
    )
    op.drop_column("lesson_schedule_entries", "class_group_id")

    op.drop_constraint("fk_tasks_class_group_id", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_class_group_id", "tasks")
    op.drop_constraint("fk_tasks_base_task_id", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_base_task_id", "tasks")
    op.drop_column("tasks", "class_group_id")
    op.drop_column("tasks", "base_task_id")

    op.drop_table("class_groups")
