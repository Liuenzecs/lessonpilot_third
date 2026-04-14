from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.core.db import reset_engine
from app.main import create_app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    runtime_dir = Path(__file__).parent / ".runtime"
    runtime_dir.mkdir(exist_ok=True)
    database_path = runtime_dir / f"lessonpilot_test_{uuid4().hex}.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-with-32-plus-bytes")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    get_settings.cache_clear()
    engine = reset_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.create_all(engine)
    app = create_app()

    with TestClient(app) as test_client:
        yield test_client

    SQLModel.metadata.drop_all(engine)
    engine.dispose()
    if database_path.exists():
        database_path.unlink()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "name": "Teacher",
            "password": "Password123",
        },
    )
    token = register_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
