from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from alembic.config import Config
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from alembic import command
from app.core.config import get_settings

_engine = None
_engine_url: str | None = None


def _build_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=False, connect_args=connect_args)


def get_engine():
    global _engine, _engine_url
    database_url = get_settings().database_url
    if _engine is None or _engine_url != database_url:
        _engine = _build_engine(database_url)
        _engine_url = database_url
    return _engine


def reset_engine(database_url: str | None = None):
    global _engine, _engine_url
    resolved_url = database_url or get_settings().database_url
    _engine = _build_engine(resolved_url)
    _engine_url = resolved_url
    return _engine


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


def _create_alembic_config() -> Config:
    api_root = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(api_root / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(api_root / "alembic"))
    alembic_config.set_main_option("sqlalchemy.url", get_settings().database_url)
    return alembic_config


def _infer_existing_revision() -> str | None:
    inspector = inspect(get_engine())
    table_names = set(inspector.get_table_names())
    if "users" not in table_names:
        return None

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if (
        {"billing_orders", "billing_webhook_events", "invoice_requests", "user_subscriptions"}.issubset(table_names)
        and {"email_verified", "email_verified_at"}.issubset(user_columns)
    ):
        return "20260412_0004"

    if (
        {"email_verified", "email_verified_at"}.issubset(user_columns)
        and {"auth_tokens", "feedback_entries"}.issubset(table_names)
    ):
        return "20260411_0003"

    if "document_snapshots" in table_names:
        return "20260411_0002"

    if {"users", "tasks", "documents"}.issubset(table_names):
        return "20260410_0001"

    return None


def run_migrations() -> None:
    alembic_config = _create_alembic_config()
    existing_revision = _infer_existing_revision()
    if existing_revision is not None:
        command.stamp(alembic_config, existing_revision)
    command.upgrade(alembic_config, "head")


def create_db_and_tables() -> None:
    from app.models import (  # noqa: F401
        AuthToken,
        BillingOrder,
        BillingWebhookEvent,
        Document,
        DocumentSnapshot,
        Feedback,
        InvoiceRequest,
        Task,
        User,
        UserSubscription,
    )

    run_migrations()
    SQLModel.metadata.create_all(get_engine())
