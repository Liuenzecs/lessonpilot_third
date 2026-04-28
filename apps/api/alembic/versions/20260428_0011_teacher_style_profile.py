"""teacher_style_profile

Revision ID: 0011_teacher_style_profile
Revises: 0010_phase7_10_asset_loop
Create Date: 2026-04-28 20:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op


revision = "0011_teacher_style_profile"
down_revision = "0010_phase7_10_asset_loop"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "teacher_style_profiles",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("objective_style", sa.Text(), nullable=False),
        sa.Column("process_style", sa.Text(), nullable=False),
        sa.Column("school_wording", sa.Text(), nullable=False),
        sa.Column("activity_preferences", sa.Text(), nullable=False),
        sa.Column("avoid_phrases", sa.Text(), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teacher_style_profiles_user_id"), "teacher_style_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_teacher_style_profiles_user_id"), table_name="teacher_style_profiles")
    op.drop_table("teacher_style_profiles")
