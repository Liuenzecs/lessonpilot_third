"""phase6 operations tables

Revision ID: 20260412_0005
Revises: 20260412_0004
Create Date: 2026-04-12 18:20:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260412_0005"
down_revision = "20260412_0004"
branch_labels = None
depends_on = None


def _uuid_type() -> sa.TypeEngine:
    return sa.String(length=36)


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    if not _has_table("analytics_events"):
        op.create_table(
            "analytics_events",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("event_name", sa.String(length=80), nullable=False),
            sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("source", sa.String(length=16), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=True),
            sa.Column("anonymous_id", sa.String(length=64), nullable=True),
            sa.Column("session_id", sa.String(length=64), nullable=False),
            sa.Column("page_path", sa.String(length=500), nullable=False),
            sa.Column("referrer", sa.Text(), nullable=True),
            sa.Column("properties", sa.JSON(), nullable=False),
            sa.Column("client_event_id", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("client_event_id"),
        )

    for index_name, columns in (
        ("ix_analytics_events_event_name", ["event_name"]),
        ("ix_analytics_events_source", ["source"]),
        ("ix_analytics_events_anonymous_id", ["anonymous_id"]),
        ("ix_analytics_events_session_id", ["session_id"]),
        ("ix_analytics_events_client_event_id", ["client_event_id"]),
    ):
        if not _has_index("analytics_events", index_name):
            op.create_index(index_name, "analytics_events", columns, unique=False)

    if not _has_table("quota_adjustments"):
        op.create_table(
            "quota_adjustments",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=False),
            sa.Column("applied_by_user_id", _uuid_type(), nullable=False),
            sa.Column("month_key", sa.String(length=7), nullable=False),
            sa.Column("delta", sa.Integer(), nullable=False),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["applied_by_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    for index_name, columns in (
        ("ix_quota_adjustments_user_id", ["user_id"]),
        ("ix_quota_adjustments_month_key", ["month_key"]),
    ):
        if not _has_index("quota_adjustments", index_name):
            op.create_index(index_name, "quota_adjustments", columns, unique=False)

    if not _has_table("email_delivery_logs"):
        op.create_table(
            "email_delivery_logs",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=True),
            sa.Column("template_key", sa.String(length=64), nullable=False),
            sa.Column("recipient_email", sa.String(length=255), nullable=False),
            sa.Column("subject", sa.String(length=255), nullable=False),
            sa.Column("delivery_mode", sa.String(length=16), nullable=False),
            sa.Column("status", sa.String(length=16), nullable=False),
            sa.Column("dedupe_key", sa.String(length=160), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    for index_name, columns in (
        ("ix_email_delivery_logs_template_key", ["template_key"]),
        ("ix_email_delivery_logs_recipient_email", ["recipient_email"]),
        ("ix_email_delivery_logs_status", ["status"]),
        ("ix_email_delivery_logs_dedupe_key", ["dedupe_key"]),
    ):
        if not _has_index("email_delivery_logs", index_name):
            op.create_index(index_name, "email_delivery_logs", columns, unique=False)


def downgrade() -> None:
    for index_name in (
        "ix_email_delivery_logs_dedupe_key",
        "ix_email_delivery_logs_status",
        "ix_email_delivery_logs_recipient_email",
        "ix_email_delivery_logs_template_key",
    ):
        op.drop_index(index_name, table_name="email_delivery_logs")
    op.drop_table("email_delivery_logs")

    for index_name in ("ix_quota_adjustments_month_key", "ix_quota_adjustments_user_id"):
        op.drop_index(index_name, table_name="quota_adjustments")
    op.drop_table("quota_adjustments")

    for index_name in (
        "ix_analytics_events_client_event_id",
        "ix_analytics_events_session_id",
        "ix_analytics_events_anonymous_id",
        "ix_analytics_events_source",
        "ix_analytics_events_event_name",
    ):
        op.drop_index(index_name, table_name="analytics_events")
    op.drop_table("analytics_events")
