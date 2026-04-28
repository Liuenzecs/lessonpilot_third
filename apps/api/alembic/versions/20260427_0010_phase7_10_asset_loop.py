"""phase7_10_asset_loop

Revision ID: 0010_phase7_10_asset_loop
Revises: 0009_rag_knowledge_chunks
Create Date: 2026-04-27 10:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel
from alembic import op


revision = "0010_phase7_10_asset_loop"
down_revision = "0009_rag_knowledge_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("templates", sa.Column("user_id", sa.String(length=36), nullable=True))
    op.create_index(op.f("ix_templates_user_id"), "templates", ["user_id"], unique=False)
    op.create_foreign_key("fk_templates_user_id", "templates", "users", ["user_id"], ["id"])

    op.create_table(
        "personal_assets",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("source_filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=16), nullable=False),
        sa.Column("subject", sa.String(length=80), nullable=False),
        sa.Column("grade", sa.String(length=80), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("extracted_content", sa.JSON(), nullable=False),
        sa.Column("reuse_suggestions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_personal_assets_asset_type"), "personal_assets", ["asset_type"], unique=False)
    op.create_index(op.f("ix_personal_assets_grade"), "personal_assets", ["grade"], unique=False)
    op.create_index(op.f("ix_personal_assets_subject"), "personal_assets", ["subject"], unique=False)
    op.create_index(op.f("ix_personal_assets_user_id"), "personal_assets", ["user_id"], unique=False)

    op.create_table(
        "teaching_packages",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teaching_packages_document_id"), "teaching_packages", ["document_id"], unique=False)
    op.create_index(op.f("ix_teaching_packages_task_id"), "teaching_packages", ["task_id"], unique=False)
    op.create_index(op.f("ix_teaching_packages_user_id"), "teaching_packages", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_teaching_packages_user_id"), table_name="teaching_packages")
    op.drop_index(op.f("ix_teaching_packages_task_id"), table_name="teaching_packages")
    op.drop_index(op.f("ix_teaching_packages_document_id"), table_name="teaching_packages")
    op.drop_table("teaching_packages")
    op.drop_index(op.f("ix_personal_assets_user_id"), table_name="personal_assets")
    op.drop_index(op.f("ix_personal_assets_subject"), table_name="personal_assets")
    op.drop_index(op.f("ix_personal_assets_grade"), table_name="personal_assets")
    op.drop_index(op.f("ix_personal_assets_asset_type"), table_name="personal_assets")
    op.drop_table("personal_assets")
    op.drop_constraint("fk_templates_user_id", "templates", type_="foreignkey")
    op.drop_index(op.f("ix_templates_user_id"), table_name="templates")
    op.drop_column("templates", "user_id")
