"""phase4 billing tables

Revision ID: 20260412_0004
Revises: 20260411_0003
Create Date: 2026-04-12 11:30:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260412_0004"
down_revision = "20260411_0003"
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
    if not _has_table("user_subscriptions"):
        op.create_table(
            "user_subscriptions",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=False),
            sa.Column("plan", sa.String(length=32), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("billing_cycle", sa.String(length=16), nullable=True),
            sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
            sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
            sa.Column("trial_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )

    if not _has_index("user_subscriptions", "ix_user_subscriptions_user_id"):
        op.create_index("ix_user_subscriptions_user_id", "user_subscriptions", ["user_id"], unique=False)

    if not _has_table("billing_orders"):
        op.create_table(
            "billing_orders",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=False),
            sa.Column("subscription_id", _uuid_type(), nullable=True),
            sa.Column("plan", sa.String(length=32), nullable=False),
            sa.Column("billing_cycle", sa.String(length=16), nullable=False),
            sa.Column("channel", sa.String(length=16), nullable=False),
            sa.Column("amount_cents", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("checkout_url", sa.Text(), nullable=True),
            sa.Column("external_order_id", sa.String(length=120), nullable=True),
            sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["subscription_id"], ["user_subscriptions.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("external_order_id"),
        )

    if not _has_index("billing_orders", "ix_billing_orders_user_id"):
        op.create_index("ix_billing_orders_user_id", "billing_orders", ["user_id"], unique=False)
    if not _has_index("billing_orders", "ix_billing_orders_subscription_id"):
        op.create_index("ix_billing_orders_subscription_id", "billing_orders", ["subscription_id"], unique=False)
    if not _has_index("billing_orders", "ix_billing_orders_external_order_id"):
        op.create_index("ix_billing_orders_external_order_id", "billing_orders", ["external_order_id"], unique=False)

    if not _has_table("billing_webhook_events"):
        op.create_table(
            "billing_webhook_events",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("event_id", sa.String(length=120), nullable=False),
            sa.Column("event_type", sa.String(length=64), nullable=False),
            sa.Column("channel", sa.String(length=16), nullable=True),
            sa.Column("signature_valid", sa.Boolean(), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("event_id"),
        )

    if not _has_index("billing_webhook_events", "ix_billing_webhook_events_event_id"):
        op.create_index("ix_billing_webhook_events_event_id", "billing_webhook_events", ["event_id"], unique=False)

    if not _has_table("invoice_requests"):
        op.create_table(
            "invoice_requests",
            sa.Column("id", _uuid_type(), nullable=False),
            sa.Column("user_id", _uuid_type(), nullable=False),
            sa.Column("order_id", _uuid_type(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("tax_number", sa.String(length=64), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["order_id"], ["billing_orders.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_index("invoice_requests", "ix_invoice_requests_user_id"):
        op.create_index("ix_invoice_requests_user_id", "invoice_requests", ["user_id"], unique=False)
    if not _has_index("invoice_requests", "ix_invoice_requests_order_id"):
        op.create_index("ix_invoice_requests_order_id", "invoice_requests", ["order_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_invoice_requests_order_id", table_name="invoice_requests")
    op.drop_index("ix_invoice_requests_user_id", table_name="invoice_requests")
    op.drop_table("invoice_requests")

    op.drop_index("ix_billing_webhook_events_event_id", table_name="billing_webhook_events")
    op.drop_table("billing_webhook_events")

    op.drop_index("ix_billing_orders_external_order_id", table_name="billing_orders")
    op.drop_index("ix_billing_orders_subscription_id", table_name="billing_orders")
    op.drop_index("ix_billing_orders_user_id", table_name="billing_orders")
    op.drop_table("billing_orders")

    op.drop_index("ix_user_subscriptions_user_id", table_name="user_subscriptions")
    op.drop_table("user_subscriptions")
