from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

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


def create_db_and_tables() -> None:
    from app.models import Document, DocumentSnapshot, Task, User  # noqa: F401

    SQLModel.metadata.create_all(get_engine())
