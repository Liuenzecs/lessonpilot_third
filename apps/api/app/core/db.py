from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from alembic.config import Config
from sqlmodel import Session, create_engine

from alembic import command
from app.core.config import get_settings

_engine = None
_engine_url: str | None = None


def _build_engine(database_url: str):
    settings = get_settings()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine_kwargs = {
        "echo": False,
        "connect_args": connect_args,
    }
    if not database_url.startswith("sqlite"):
        engine_kwargs.update(
            {
                "pool_pre_ping": True,
                "pool_size": settings.db_pool_size,
                "max_overflow": settings.db_max_overflow,
                "pool_timeout": settings.db_pool_timeout,
                "pool_recycle": settings.db_pool_recycle,
            }
        )
    return create_engine(database_url, **engine_kwargs)


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


def run_migrations() -> None:
    alembic_config = _create_alembic_config()
    command.upgrade(alembic_config, "head")


def create_db_and_tables() -> None:
    database_url = get_settings().database_url
    if database_url.startswith("sqlite"):
        return
    run_migrations()
