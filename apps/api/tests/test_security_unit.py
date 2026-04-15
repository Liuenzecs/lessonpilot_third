"""单元测试：core/security.py"""

from __future__ import annotations

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_bcrypt_hash():
    result = hash_password("MyPassword123")
    assert result.startswith("$2")
    assert result != "MyPassword123"


def test_verify_password_correct():
    hashed = hash_password("MyPassword123")
    assert verify_password("MyPassword123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("MyPassword123")
    assert verify_password("WrongPassword", hashed) is False


def test_create_and_decode_access_token(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-with-32-plus-bytes")
    from app.core.config import get_settings
    get_settings.cache_clear()

    token = create_access_token("user-123")
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert "exp" in payload
    get_settings.cache_clear()


def test_decode_invalid_token_raises_401(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-with-32-plus-bytes")
    from app.core.config import get_settings
    get_settings.cache_clear()

    with pytest.raises(Exception) as exc_info:
        decode_access_token("this-is-not-a-valid-token")
    assert exc_info.value.status_code == 401
    get_settings.cache_clear()


def test_hash_password_different_each_time():
    """bcrypt salt 应使每次哈希不同。"""
    h1 = hash_password("same-password")
    h2 = hash_password("same-password")
    assert h1 != h2
    # 但两个都能验证
    assert verify_password("same-password", h1)
    assert verify_password("same-password", h2)
