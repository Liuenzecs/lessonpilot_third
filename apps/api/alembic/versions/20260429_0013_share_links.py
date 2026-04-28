"""share links

Revision ID: 0013
Revises: 0012_question_bank
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0013_share_links"
down_revision: str | None = "0012_question_bank"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "share_links",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.String(36), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("permission", sa.String(16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_share_links_document_id", "share_links", ["document_id"])
    op.create_index("ix_share_links_owner_id", "share_links", ["owner_id"])
    op.create_index("ix_share_links_token", "share_links", ["token"], unique=True)

    op.create_table(
        "share_comments",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("share_link_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("author_name", sa.String(100), nullable=False),
        sa.Column("section_name", sa.String(64), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["share_link_id"], ["share_links.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_share_comments_share_link_id", "share_comments", ["share_link_id"])
    op.create_index("ix_share_comments_user_id", "share_comments", ["user_id"])


def downgrade() -> None:
    op.drop_table("share_comments")
    op.drop_table("share_links")
